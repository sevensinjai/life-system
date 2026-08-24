"""Motivational quotes the player writes for themselves."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.player import Player


class Quote(Base):
    """One line the player wants thrown back at them on a future morning.

    A quote is a pool entry, not a schedule: the player writes as many as they
    like and the System surfaces one per local day. Nothing is shared or
    published — a quote belongs to whoever wrote it, like a quest.
    """

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    # Stored with whitespace already collapsed, so two copies of the same line
    # compare equal when the collection is deduplicated.
    text: Mapped[str] = mapped_column(Text)
    # Who said it, if anyone did. Null for something the player wrote.
    author: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Archived quotes drop out of the rotation but keep their row, so a widget
    # still holding yesterday's id can resolve it instead of erroring.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    player: Mapped["Player"] = relationship(back_populates="quotes")

    def __repr__(self) -> str:
        return f"<Quote id={self.id} text={self.text[:32]!r}>"
