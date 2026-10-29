import hashlib
import secrets

from psycopg import errors
from werkzeug import security

from vgm import common
from vgm import contracts
from vgm.generated import vgm_pb2_grpc

PUBLIC_COLUMNS = "id, username, display_name, bio, created_at"
DUMMY_HASH = security.generate_password_hash("constant-unused-password")


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


class Identity(vgm_pb2_grpc.IdentityServicer):

    def __init__(self, pool):
        self.pool = pool

    def session(self, conn, user):
        token = secrets.token_urlsafe(32)
        conn.execute("DELETE FROM identity.sessions WHERE expires_at < now()")
        conn.execute(
            "INSERT INTO identity.sessions (token_hash, user_id) "
            "VALUES (%s, %s)",
            (digest(token), user["id"]),
        )
        return {"user": user, "token": token}

    @common.rpc(contracts.Register)
    def Register(self, data):
        password_hash = security.generate_password_hash(data.password)
        query = f"""
            INSERT INTO identity.users (username, display_name, password_hash)
            VALUES (%s, %s, %s)
            RETURNING {PUBLIC_COLUMNS}
        """
        parameters = (data.username, data.display_name, password_hash)

        try:
            with self.pool.connection() as conn:
                user = conn.execute(query, parameters).fetchone()
                return self.session(conn, user)
        except errors.UniqueViolation:
            raise common.AppError(
                409, "That username is already taken"
            ) from None

    @common.rpc(contracts.Credentials)
    def Login(self, data):
        query = f"""
            SELECT {PUBLIC_COLUMNS}, password_hash
            FROM identity.users
            WHERE username = %s
        """
        with self.pool.connection() as conn:
            user = conn.execute(query, (data.username,)).fetchone()
            password_hash = user["password_hash"] if user else DUMMY_HASH
            valid = security.check_password_hash(password_hash, data.password)
            if not user or not valid:
                raise common.AppError(401, "Incorrect username or password")

            del user["password_hash"]
            return self.session(conn, user)

    @common.rpc(contracts.Token)
    def Authenticate(self, data):
        query = """
            SELECT u.id, u.username, u.display_name, u.bio, u.created_at
            FROM identity.users u
            JOIN identity.sessions s ON s.user_id = u.id
            WHERE s.token_hash = %s AND s.expires_at > now()
        """
        with self.pool.connection() as conn:
            user = conn.execute(query, (digest(data.token),)).fetchone()

        if not user:
            raise common.AppError(
                401, "Your session has expired. Please sign in again"
            )

        return user

    @common.rpc(contracts.Token)
    def Logout(self, data):
        with self.pool.connection() as conn:
            conn.execute(
                "DELETE FROM identity.sessions WHERE token_hash = %s",
                (digest(data.token),),
            )

        return {"ok": True}

    @common.rpc(contracts.Search)
    def Search(self, data):
        escaped = data.query.replace("\\", "\\\\")
        escaped = escaped.replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        query = f"""
            SELECT {PUBLIC_COLUMNS}
            FROM identity.users
            WHERE id <> %s AND (username ILIKE %s OR display_name ILIKE %s)
            ORDER BY username
            LIMIT 30
        """
        with self.pool.connection() as conn:
            parameters = (data.actor_id, pattern, pattern)
            users = conn.execute(query, parameters).fetchall()

        return {"users": users}

    @common.rpc(contracts.Profiles)
    def Profiles(self, data):
        query = (
            f"SELECT {PUBLIC_COLUMNS} FROM identity.users "
            "WHERE id = ANY(%s)"
        )
        with self.pool.connection() as conn:
            users = conn.execute(query, (data.ids,)).fetchall()

        return {"users": users}

    @common.rpc(contracts.UpdateProfile)
    def UpdateProfile(self, data):
        query = f"""
            UPDATE identity.users
            SET display_name = %s, bio = %s
            WHERE id = %s
            RETURNING {PUBLIC_COLUMNS}
        """
        parameters = (data.display_name, data.bio, data.actor_id)
        with self.pool.connection() as conn:
            user = conn.execute(query, parameters).fetchone()

        if not user:
            raise common.AppError(404, "User not found")

        return user
