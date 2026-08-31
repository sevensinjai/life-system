"""persist skill practice journal entries and attachments

Revision ID: e14a8c61d920
Revises: 4d8b6a10c2ef
Create Date: 2026-08-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e14a8c61d920"
down_revision: Union[str, Sequence[str], None] = "4d8b6a10c2ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "practice_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("minutes", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_practice_entries_player_id", "practice_entries", ["player_id"])
    op.create_index("ix_practice_entries_skill_id", "practice_entries", ["skill_id"])
    op.create_index("ix_practice_entries_created_at", "practice_entries", ["created_at"])
    op.create_table(
        "practice_attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_id", sa.Integer(), sa.ForeignKey("practice_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=12), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("byte_count", sa.Integer(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
    )
    op.create_index("ix_practice_attachments_entry_id", "practice_attachments", ["entry_id"])


def downgrade() -> None:
    op.drop_table("practice_attachments")
    op.drop_table("practice_entries")
