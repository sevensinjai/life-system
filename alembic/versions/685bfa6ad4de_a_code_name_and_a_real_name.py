"""a code name and a real name

A constellation has two names, and until now the table held one.

* ``code_name`` — what it is called: a title, grand and impersonal, and the
  name it speaks under. This is the old ``name`` column, renamed for what it
  actually held.
* ``real_name`` — who it was before it was a constellation. New, and null
  until the pantheon is seeded.
* Both, plus ``epithet``, gain a ``_zh_hant`` twin. Names are the one part of
  this content that is bilingual today; the voices and the trials are still
  English-only until the localization pass.

The old ``name`` is copied into ``code_name`` rather than dropped, so an
existing row survives the upgrade with the name it had. It will read as the
old long form — "The Constellation of the Fallen Star" — until the pantheon is
re-seeded:

    .venv/bin/python -m scripts.seed_pantheon

which fills in every name in both scripts. Seeding matches on ``code``, so
favor rows and friendships are untouched by the rewrite.

Revision ID: 685bfa6ad4de
Revises: 126434707086
Create Date: 2026-08-24 13:24:47.905612

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "685bfa6ad4de"
down_revision: Union[str, Sequence[str], None] = "126434707086"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("constellations", schema=None) as batch_op:
        # Added with a default so it can be NOT NULL on a populated table; the
        # copy below gives every existing row its real value.
        batch_op.add_column(
            sa.Column(
                "code_name",
                sa.String(length=120),
                nullable=False,
                server_default="",
            )
        )
        batch_op.add_column(
            sa.Column("code_name_zh_hant", sa.String(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("real_name", sa.String(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("real_name_zh_hant", sa.String(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("epithet_zh_hant", sa.String(length=200), nullable=True)
        )

    op.execute(sa.text("UPDATE constellations SET code_name = name"))

    with op.batch_alter_table("constellations", schema=None) as batch_op:
        batch_op.drop_column("name")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("constellations", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("name", sa.String(length=120), nullable=False, server_default="")
        )

    op.execute(sa.text("UPDATE constellations SET name = code_name"))

    with op.batch_alter_table("constellations", schema=None) as batch_op:
        batch_op.drop_column("epithet_zh_hant")
        batch_op.drop_column("real_name_zh_hant")
        batch_op.drop_column("real_name")
        batch_op.drop_column("code_name_zh_hant")
        batch_op.drop_column("code_name")
