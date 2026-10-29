from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE SCHEMA identity;
        CREATE SCHEMA messaging;
        CREATE TABLE identity.users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            username varchar(32) NOT NULL UNIQUE,
            display_name varchar(60) NOT NULL,
            password_hash text NOT NULL,
            bio varchar(280) NOT NULL DEFAULT '',
            created_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE TABLE identity.sessions (
            token_hash char(64) PRIMARY KEY,
            user_id uuid NOT NULL
                REFERENCES identity.users(id) ON DELETE CASCADE,
            expires_at timestamptz NOT NULL DEFAULT now() + interval '7 days'
        );
        CREATE INDEX sessions_expiry ON identity.sessions(expires_at);
        CREATE TABLE messaging.conversations (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_a uuid NOT NULL,
            user_b uuid NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (user_a, user_b),
            CHECK (user_a < user_b)
        );
        CREATE INDEX conversations_user_a
            ON messaging.conversations(user_a, updated_at DESC);
        CREATE INDEX conversations_user_b
            ON messaging.conversations(user_b, updated_at DESC);
        CREATE TABLE messaging.messages (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            conversation_id uuid NOT NULL
                REFERENCES messaging.conversations(id) ON DELETE CASCADE,
            sender_id uuid NOT NULL,
            client_id uuid NOT NULL,
            kind text NOT NULL CHECK (kind IN ('text', 'video')),
            text varchar(4000) NOT NULL DEFAULT '',
            video jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (conversation_id, sender_id, client_id),
            CHECK (
                (kind = 'text' AND length(text) > 0 AND video IS NULL)
                OR (kind = 'video' AND video IS NOT NULL)
            )
        );
        CREATE INDEX messages_conversation
            ON messaging.messages(conversation_id, id DESC);
    """
    )


def downgrade():
    op.execute("DROP SCHEMA messaging CASCADE; DROP SCHEMA identity CASCADE;")
