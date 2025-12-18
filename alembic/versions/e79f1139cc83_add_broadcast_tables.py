"""add_broadcast_tables

Revision ID: e79f1139cc83
Revises: 27da68d2ec61
Create Date: 2025-12-18 13:52:14.585359

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e79f1139cc83'
down_revision: Union[str, None] = '27da68d2ec61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS broadcast_campaigns (
            id SERIAL PRIMARY KEY,
            admin_id BIGINT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'created',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            scheduled_at TIMESTAMPTZ
        );

        CREATE TABLE IF NOT EXISTS broadcast_messages (
            id SERIAL PRIMARY KEY,
            campaign_id INTEGER NOT NULL REFERENCES broadcast_campaigns(id) ON DELETE CASCADE,
            language_code VARCHAR(10) NOT NULL,
            content_type VARCHAR(20) NOT NULL,
            file_id TEXT,
            text TEXT,
            caption TEXT,
            reply_markup JSONB
        );
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE IF EXISTS broadcast_messages;
        DROP TABLE IF EXISTS broadcast_campaigns;
    """)
