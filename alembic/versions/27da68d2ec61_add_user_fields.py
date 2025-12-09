"""add_user_fields

Revision ID: 27da68d2ec61
Revises: b20e5643d3bd
Create Date: 2025-12-09 16:51:12.481071

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '27da68d2ec61'
down_revision: Union[str, None] = 'b20e5643d3bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import sqlalchemy as sa


def upgrade() -> None:
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'username')
