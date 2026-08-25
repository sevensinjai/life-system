"""merge skill graph and friendship migration heads

Revision ID: 9f4c2d8a71be
Revises: 126434707086, c7a2e5f1b840
Create Date: 2026-08-25
"""

from typing import Sequence, Union


revision: str = "9f4c2d8a71be"
down_revision: Union[str, Sequence[str], None] = (
    "126434707086",
    "c7a2e5f1b840",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Join the two additive schema branches."""


def downgrade() -> None:
    """Split back to the two parent revisions."""
