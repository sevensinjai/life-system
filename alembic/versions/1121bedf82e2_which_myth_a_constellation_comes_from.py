"""which myth a constellation comes from

Adds ``constellations.tradition``: greek, chinese or japanese.

Stored rather than derived from the catalog, because a pantheon of this size
is read grouped — `GET /constellations?tradition=` — and because a client
showing a constellation has no way to consult a Python module.

Existing rows take ``greek`` from the server default, which is wrong for two
thirds of them; re-seed to correct it, as with any content change:

    .venv/bin/python -m scripts.seed_pantheon

Revision ID: 1121bedf82e2
Revises: 685bfa6ad4de
Create Date: 2026-08-24 14:02:19.771634

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "1121bedf82e2"
down_revision: Union[str, Sequence[str], None] = "685bfa6ad4de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("constellations", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "tradition",
                sa.String(length=16),
                nullable=False,
                server_default="greek",
            )
        )
        batch_op.create_index(
            batch_op.f("ix_constellations_tradition"), ["tradition"]
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("constellations", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_constellations_tradition"))
        batch_op.drop_column("tradition")
