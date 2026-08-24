"""befriending a constellation

A constellation issues trials to its friends and to nobody else, and this is
how one becomes a friend: you ask, it may set you a trial of admission, and
clearing that trial opens the channel.

* ``friendship_requests`` — every request, refusals included. A log: the
  verdict, what the player said for themselves, and the trial that was set.
  Kept because an arbiter that reads a request rather than rolling for it will
  want the history.
* ``constellation_favor`` — gains ``is_friend``, the two dates around it, and
  ``may_ask_after``: the wait before this player may ask this constellation
  again. The wait sits on the pair rather than on any one request, because
  that is what it is about — these two, and how soon they may speak again.
  Standing and friendship stay separate: favor is what a constellation thinks
  of you, friendship is whether it speaks to you at all.
* ``side_quests.is_challenge`` — marks a trial addressed to one player rather
  than broadcast. Every path that reaches all players filters it out.

Additive. Existing rows default to ``is_friend`` false and ``is_challenge``
false, which is the right reading of both: nobody was a friend before there
was friendship, and every side quest so far was a broadcast.

Revision ID: 126434707086
Revises: b0784d0632c4
Create Date: 2026-08-24 13:12:54.334447

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "126434707086"
down_revision: Union[str, Sequence[str], None] = "b0784d0632c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "friendship_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("constellation_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("verdict_reason", sa.Text(), nullable=True),
        sa.Column("challenge_offer_id", sa.Integer(), nullable=True),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["challenge_offer_id"], ["side_quest_offers.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["constellation_id"], ["constellations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("friendship_requests", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_friendship_requests_constellation_id"), ["constellation_id"]
        )
        batch_op.create_index(
            batch_op.f("ix_friendship_requests_player_id"), ["player_id"]
        )
        batch_op.create_index(
            batch_op.f("ix_friendship_requests_requested_at"), ["requested_at"]
        )
        batch_op.create_index(
            batch_op.f("ix_friendship_requests_status"), ["status"]
        )

    with op.batch_alter_table("constellation_favor", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_friend", sa.Boolean(), nullable=False, server_default=sa.false()
            )
        )
        batch_op.add_column(
            sa.Column("befriended_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("unfriended_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column("may_ask_after", sa.DateTime(timezone=True), nullable=True)
        )

    with op.batch_alter_table("side_quests", schema=None) as batch_op:
        # Everything sent before this revision was, in fact, a broadcast.
        batch_op.add_column(
            sa.Column(
                "is_challenge", sa.Boolean(), nullable=False, server_default=sa.false()
            )
        )
        batch_op.create_index(
            batch_op.f("ix_side_quests_is_challenge"), ["is_challenge"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("side_quests", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_side_quests_is_challenge"))
        batch_op.drop_column("is_challenge")

    with op.batch_alter_table("constellation_favor", schema=None) as batch_op:
        batch_op.drop_column("may_ask_after")
        batch_op.drop_column("unfriended_at")
        batch_op.drop_column("befriended_at")
        batch_op.drop_column("is_friend")

    with op.batch_alter_table("friendship_requests", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_friendship_requests_status"))
        batch_op.drop_index(batch_op.f("ix_friendship_requests_requested_at"))
        batch_op.drop_index(batch_op.f("ix_friendship_requests_player_id"))
        batch_op.drop_index(batch_op.f("ix_friendship_requests_constellation_id"))

    op.drop_table("friendship_requests")
