"""skill graph

Adds the skills table — a self-referential tree of what the player trains —
and the two columns that let a quest train one.

Purely additive. Existing quests get skill_id NULL and skill_exp_reward 0,
which is exactly "this quest trains nothing", so no behaviour changes for
anything already authored.

The self-referential FK is created inside the CREATE TABLE rather than added
afterwards: SQLite cannot ALTER a table to add a foreign key, and batch mode
would otherwise have to rebuild the table it had just made.

Revision ID: c7a2e5f1b840
Revises: b3f1c07a92d4
Create Date: 2026-08-24 12:41:07.553901

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c7a2e5f1b840"
down_revision: Union[str, Sequence[str], None] = "b3f1c07a92d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("exp", sa.Integer(), nullable=False),
        sa.Column("total_exp_earned", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("skills", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_skills_player_id"), ["player_id"])
        batch_op.create_index(batch_op.f("ix_skills_parent_id"), ["parent_id"])

    with op.batch_alter_table("quests", schema=None) as batch_op:
        batch_op.add_column(sa.Column("skill_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "skill_exp_reward",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch_op.create_index(batch_op.f("ix_quests_skill_id"), ["skill_id"])
        batch_op.create_foreign_key(
            batch_op.f("fk_quests_skill_id_skills"),
            "skills",
            ["skill_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("quests", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_quests_skill_id_skills"), type_="foreignkey"
        )
        batch_op.drop_index(batch_op.f("ix_quests_skill_id"))
        batch_op.drop_column("skill_exp_reward")
        batch_op.drop_column("skill_id")

    with op.batch_alter_table("skills", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_skills_parent_id"))
        batch_op.drop_index(batch_op.f("ix_skills_player_id"))

    op.drop_table("skills")
