"""player quote collection

Adds the quotes table: the pool of motivational lines a player writes for
themselves, one of which the lock-screen widget shows per local day.

Purely additive — no existing table is touched, and which quote a given day
lands on is computed from the pool rather than stored, so there is nothing to
backfill.

Revision ID: b3f1c07a92d4
Revises: afff1562526e
Create Date: 2026-08-24 12:05:41.220718

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3f1c07a92d4"
down_revision: Union[str, Sequence[str], None] = "afff1562526e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("author", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("quotes", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_quotes_player_id"), ["player_id"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("quotes", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_quotes_player_id"))

    op.drop_table("quotes")
