"""the pantheon behind side quests

Gives side quests an author and a memory.

* ``constellations`` — the cast that issues broadcasts, seeded from
  ``app/content/pantheon.py`` by ``scripts/seed_pantheon.py``. Keyed by a
  stable ``code`` so a rewritten name or voice updates the row in place.
* ``constellation_favor`` — what one constellation makes of one player. The
  standing band is derived from ``favor`` rather than stored, so retuning the
  thresholds needs no migration.
* ``side_quests`` — gains ``constellation_id`` (who issued it),
  ``catalog_code`` (which written trial it came from, so the scheduler can
  rotate), ``lines`` (per-trial overrides for the constellation's voice), and
  ``min_standing`` (a trial reserved for players who earned it).

``side_quests.herald`` is dropped: a free-text name is exactly what the
constellations table replaces. It shipped one revision ago and nothing
populated it, so there is nothing to carry across; a deployment that did fill
it in should map those strings to constellation codes before upgrading.

Revision ID: b0784d0632c4
Revises: c7d2ae51f930
Create Date: 2026-08-24 12:39:03.422577

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b0784d0632c4"
down_revision: Union[str, Sequence[str], None] = "c7d2ae51f930"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_SIDE_QUEST_CONSTELLATION = "fk_side_quests_constellation_id"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "constellations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("epithet", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", sa.String(length=16), nullable=True),
        sa.Column("voice", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("constellations", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_constellations_code"), ["code"], unique=True
        )

    op.create_table(
        "constellation_favor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("constellation_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("favor", sa.Integer(), nullable=False),
        sa.Column("offers_received", sa.Integer(), nullable=False),
        sa.Column("completed", sa.Integer(), nullable=False),
        sa.Column("declined", sa.Integer(), nullable=False),
        sa.Column("expired", sa.Integer(), nullable=False),
        sa.Column("failed", sa.Integer(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["constellation_id"], ["constellations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "constellation_id", "player_id", name="uq_favor_per_player"
        ),
    )
    with op.batch_alter_table("constellation_favor", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_constellation_favor_constellation_id"),
            ["constellation_id"],
        )
        batch_op.create_index(
            batch_op.f("ix_constellation_favor_player_id"), ["player_id"]
        )

    with op.batch_alter_table("side_quests", schema=None) as batch_op:
        batch_op.add_column(sa.Column("constellation_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("catalog_code", sa.String(length=64), nullable=True)
        )
        # Server default so the column can be NOT NULL on a table that already
        # has rows; a broadcast with no overrides carries an empty object.
        batch_op.add_column(
            sa.Column(
                "lines", sa.JSON(), nullable=False, server_default=sa.text("'{}'")
            )
        )
        batch_op.add_column(
            sa.Column("min_standing", sa.String(length=16), nullable=True)
        )
        batch_op.create_index(
            batch_op.f("ix_side_quests_catalog_code"), ["catalog_code"]
        )
        batch_op.create_index(
            batch_op.f("ix_side_quests_constellation_id"), ["constellation_id"]
        )
        batch_op.create_foreign_key(
            FK_SIDE_QUEST_CONSTELLATION,
            "constellations",
            ["constellation_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.drop_column("herald")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("side_quests", schema=None) as batch_op:
        batch_op.add_column(sa.Column("herald", sa.String(length=120), nullable=True))
        batch_op.drop_constraint(FK_SIDE_QUEST_CONSTELLATION, type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_side_quests_constellation_id"))
        batch_op.drop_index(batch_op.f("ix_side_quests_catalog_code"))
        batch_op.drop_column("min_standing")
        batch_op.drop_column("lines")
        batch_op.drop_column("catalog_code")
        batch_op.drop_column("constellation_id")

    with op.batch_alter_table("constellation_favor", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_constellation_favor_player_id"))
        batch_op.drop_index(batch_op.f("ix_constellation_favor_constellation_id"))
    op.drop_table("constellation_favor")

    with op.batch_alter_table("constellations", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_constellations_code"))
    op.drop_table("constellations")
