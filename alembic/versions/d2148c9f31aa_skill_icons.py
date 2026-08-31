"""Give every skill an optional visual identity.

Revision ID: d2148c9f31aa
Revises: e14a8c61d920
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d2148c9f31aa"
down_revision: str | Sequence[str] | None = "e14a8c61d920"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("skills", sa.Column("icon_key", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("skills", "icon_key")
