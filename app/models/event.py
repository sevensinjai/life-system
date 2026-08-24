"""The system log — the message feed the app renders as System notifications."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import EventType

if TYPE_CHECKING:
    from app.models.player import Player


class SystemEvent(Base):
    __tablename__ = "system_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, native_enum=False, length=32)
    )
    message: Mapped[str] = mapped_column(String(500))
    # Structured detail for the client to render, e.g. {"new_level": 4}.
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    player: Mapped["Player"] = relationship(back_populates="events")

    def __repr__(self) -> str:
        return f"<SystemEvent id={self.id} type={self.event_type}>"
