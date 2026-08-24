"""side quests and the opt-in that gates them

Adds three tables and one column:

* ``side_quests`` — System-issued broadcasts, one row shared by every player.
* ``side_quest_offers`` — a player's copy of a broadcast: their answer and
  their progress. Unique per (side quest, player), which is what makes
  dispatching a broadcast idempotent.
* ``side_quest_preferences`` — the opt-in. One row per player, written the
  first time they answer; no row means opted out.
* ``penalties.side_quest_offer_id`` — so an EXP loss from a lapsed side quest
  points at the offer, the way a lapsed quest period points at its instance.

Additive, and there is nothing to backfill: every existing player has no
preference row, which already reads as opted out.

Revision ID: c7d2ae51f930
Revises: b3f1c07a92d4
Create Date: 2026-08-24 12:31:08.442095

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c7d2ae51f930"
down_revision: Union[str, Sequence[str], None] = "b3f1c07a92d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "side_quests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("herald", sa.String(length=120), nullable=True),
        sa.Column("difficulty", sa.String(length=2), nullable=False),
        sa.Column("target_count", sa.Integer(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("exp_reward", sa.Integer(), nullable=False),
        sa.Column("stat_reward", sa.String(length=16), nullable=True),
        sa.Column("stat_reward_amount", sa.Integer(), nullable=False),
        sa.Column("penalty_exp", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("broadcast_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("min_level", sa.Integer(), nullable=False),
        sa.Column("max_level", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("side_quests", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_side_quests_status"), ["status"])
        batch_op.create_index(
            batch_op.f("ix_side_quests_broadcast_at"), ["broadcast_at"]
        )
        batch_op.create_index(batch_op.f("ix_side_quests_expires_at"), ["expires_at"])

    op.create_table(
        "side_quest_offers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("side_quest_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("target_count", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "offered_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["side_quest_id"], ["side_quests.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "side_quest_id", "player_id", name="uq_side_quest_offer_per_player"
        ),
    )
    with op.batch_alter_table("side_quest_offers", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_side_quest_offers_side_quest_id"), ["side_quest_id"]
        )
        batch_op.create_index(
            batch_op.f("ix_side_quest_offers_player_id"), ["player_id"]
        )
        batch_op.create_index(batch_op.f("ix_side_quest_offers_status"), ["status"])
        batch_op.create_index(
            batch_op.f("ix_side_quest_offers_expires_at"), ["expires_at"]
        )
        batch_op.create_index(
            batch_op.f("ix_side_quest_offers_offered_at"), ["offered_at"]
        )

    op.create_table(
        "side_quest_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("is_opted_in", sa.Boolean(), nullable=False),
        sa.Column("frequency", sa.String(length=16), nullable=False),
        sa.Column("max_difficulty", sa.String(length=2), nullable=True),
        sa.Column("auto_accept", sa.Boolean(), nullable=False),
        sa.Column("opted_in_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opted_out_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("side_quest_preferences", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_side_quest_preferences_player_id"),
            ["player_id"],
            unique=True,
        )

    with op.batch_alter_table("penalties", schema=None) as batch_op:
        batch_op.add_column(sa.Column("side_quest_offer_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_penalties_side_quest_offer_id",
            "side_quest_offers",
            ["side_quest_offer_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("penalties", schema=None) as batch_op:
        batch_op.drop_constraint("fk_penalties_side_quest_offer_id", type_="foreignkey")
        batch_op.drop_column("side_quest_offer_id")

    with op.batch_alter_table("side_quest_preferences", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_side_quest_preferences_player_id"))
    op.drop_table("side_quest_preferences")

    with op.batch_alter_table("side_quest_offers", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_side_quest_offers_offered_at"))
        batch_op.drop_index(batch_op.f("ix_side_quest_offers_expires_at"))
        batch_op.drop_index(batch_op.f("ix_side_quest_offers_status"))
        batch_op.drop_index(batch_op.f("ix_side_quest_offers_player_id"))
        batch_op.drop_index(batch_op.f("ix_side_quest_offers_side_quest_id"))
    op.drop_table("side_quest_offers")

    with op.batch_alter_table("side_quests", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_side_quests_expires_at"))
        batch_op.drop_index(batch_op.f("ix_side_quests_broadcast_at"))
        batch_op.drop_index(batch_op.f("ix_side_quests_status"))
    op.drop_table("side_quests")
