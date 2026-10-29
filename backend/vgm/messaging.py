from psycopg.types import json as json_types

from vgm import common
from vgm import contracts
from vgm.generated import vgm_pb2_grpc


def require_membership(conn, conversation_id, actor_id):
    query = """
        SELECT id
        FROM messaging.conversations
        WHERE id = %s AND (user_a = %s OR user_b = %s)
    """
    row = conn.execute(query, (conversation_id, actor_id, actor_id)).fetchone()
    if not row:
        raise common.AppError(404, "Conversation not found")


def previous_message(conn, data):
    query = """
        SELECT *
        FROM messaging.messages
        WHERE conversation_id = %s AND sender_id = %s AND client_id = %s
    """
    parameters = (data.conversation_id, data.actor_id, data.client_id)
    return conn.execute(query, parameters).fetchone()


class Messaging(vgm_pb2_grpc.MessagingServicer):

    def __init__(self, pool):
        self.pool = pool
        self.identity = common.client("identity")
        self.video = common.client("video")

    @common.rpc(contracts.Actor)
    def Conversations(self, data):
        query = """
            SELECT c.id,
                   CASE WHEN c.user_a = %s
                       THEN c.user_b ELSE c.user_a END AS peer_id,
                   c.updated_at,
                   m.text AS last_text,
                   m.kind AS last_kind
            FROM messaging.conversations c
            LEFT JOIN LATERAL (
                SELECT text, kind
                FROM messaging.messages
                WHERE conversation_id = c.id
                ORDER BY id DESC
                LIMIT 1
            ) m ON true
            WHERE c.user_a = %s OR c.user_b = %s
            ORDER BY c.updated_at DESC
            LIMIT 100
        """
        with self.pool.connection() as conn:
            parameters = (data.actor_id, data.actor_id, data.actor_id)
            conversations = conn.execute(query, parameters).fetchall()

        peer_ids = [conversation["peer_id"] for conversation in conversations]
        profiles = common.call(self.identity, "Profiles", {"ids": peer_ids})
        users_by_id = {user["id"]: user for user in profiles["users"]}
        for conversation in conversations:
            peer_id = str(conversation.pop("peer_id"))
            conversation["peer"] = users_by_id.get(peer_id)

        return {"conversations": conversations}

    @common.rpc(contracts.OpenConversation)
    def OpenConversation(self, data):
        if data.actor_id == data.recipient_id:
            raise common.AppError(
                422, "Choose another person to start a conversation"
            )

        profiles = common.call(
            self.identity, "Profiles", {"ids": [data.recipient_id]}
        )
        if not profiles["users"]:
            raise common.AppError(404, "User not found")

        user_a, user_b = sorted([data.actor_id, data.recipient_id])
        query = """
            INSERT INTO messaging.conversations (user_a, user_b)
            VALUES (%s, %s)
            ON CONFLICT (user_a, user_b)
                DO UPDATE SET user_a = EXCLUDED.user_a
            RETURNING id, updated_at
        """
        with self.pool.connection() as conn:
            conversation = conn.execute(query, (user_a, user_b)).fetchone()

        return {
            **conversation,
            "peer": profiles["users"][0],
            "last_text": None,
            "last_kind": None,
        }

    @common.rpc(contracts.MessageQuery)
    def Messages(self, data):
        direction = "ASC" if data.after is not None else "DESC"
        query = f"""
            SELECT id, conversation_id, sender_id, client_id,
                   kind, text, video, created_at
            FROM messaging.messages
            WHERE conversation_id = %s
                AND (%s::bigint IS NULL OR id < %s)
                AND (%s::bigint IS NULL OR id > %s)
            ORDER BY id {direction}
            LIMIT %s
        """
        parameters = (
            data.conversation_id,
            data.before,
            data.before,
            data.after,
            data.after,
            data.limit + 1,
        )
        with self.pool.connection() as conn:
            require_membership(conn, data.conversation_id, data.actor_id)
            messages = conn.execute(query, parameters).fetchall()

        has_more = len(messages) > data.limit
        messages = messages[:data.limit]
        if data.after is None:
            messages.reverse()

        return {"messages": messages, "has_more": has_more}

    @common.rpc(contracts.Send)
    def Send(self, data):
        with self.pool.connection() as conn:
            require_membership(conn, data.conversation_id, data.actor_id)
            previous = previous_message(conn, data)

        if previous:
            return previous

        video = None
        if data.kind == "video":
            video = common.call(self.video, "Resolve", {"url": data.url})

        query = """
            INSERT INTO messaging.messages (
                conversation_id, sender_id, client_id, kind, text, video
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (conversation_id, sender_id, client_id) DO NOTHING
            RETURNING *
        """
        parameters = (
            data.conversation_id,
            data.actor_id,
            data.client_id,
            data.kind,
            data.text,
            json_types.Jsonb(video) if video else None,
        )
        with self.pool.connection() as conn:
            conn.execute(
                "SELECT id FROM messaging.conversations "
                "WHERE id = %s FOR UPDATE",
                (data.conversation_id,),
            )
            message = conn.execute(query, parameters).fetchone()

            if message:
                conn.execute(
                    "UPDATE messaging.conversations "
                    "SET updated_at = now() WHERE id = %s",
                    (data.conversation_id,),
                )
            else:
                message = previous_message(conn, data)

        return message
