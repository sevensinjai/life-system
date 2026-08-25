"""make quest rewards explicit practice minutes

Revision ID: 4d8b6a10c2ef
Revises: 9f4c2d8a71be
Create Date: 2026-08-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "4d8b6a10c2ef"
down_revision: Union[str, Sequence[str], None] = "9f4c2d8a71be"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Treat existing rewards as minutes and snapshot them on open periods."""
    with op.batch_alter_table("quests") as batch_op:
        batch_op.add_column(sa.Column("units_per_minute", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column("practice_minutes", sa.Integer(), nullable=True)
        )
    op.execute(
        "UPDATE quests SET practice_minutes = CASE "
        "WHEN exp_reward > 0 THEN exp_reward ELSE 1 END"
    )
    with op.batch_alter_table("quests") as batch_op:
        batch_op.alter_column("practice_minutes", nullable=False)

    with op.batch_alter_table("quest_instances") as batch_op:
        batch_op.add_column(
            sa.Column("practice_minutes", sa.Integer(), nullable=True)
        )
    op.execute(
        "UPDATE quest_instances SET practice_minutes = COALESCE(" 
        "(SELECT CASE WHEN quests.exp_reward > 0 THEN quests.exp_reward ELSE 1 END "
        "FROM quests WHERE quests.id = quest_instances.quest_id), 1)"
    )
    with op.batch_alter_table("quest_instances") as batch_op:
        batch_op.alter_column("practice_minutes", nullable=False)

    # A skill receives the same credited minutes as the player. Keep the old
    # columns for backwards-compatible clients while they become aliases.
    op.execute(
        "UPDATE quests SET exp_reward = practice_minutes, "
        "skill_exp_reward = CASE WHEN skill_id IS NULL THEN 0 ELSE practice_minutes END"
    )


def downgrade() -> None:
    with op.batch_alter_table("quest_instances") as batch_op:
        batch_op.drop_column("practice_minutes")
    with op.batch_alter_table("quests") as batch_op:
        batch_op.drop_column("practice_minutes")
        batch_op.drop_column("units_per_minute")
