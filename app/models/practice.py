"""Persisted notes and media from hands-on skill practice."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, LargeBinary, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PracticeEntry(Base):
    __tablename__ = "practice_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), index=True
    )
    minutes: Mapped[int] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    attachments: Mapped[list["PracticeAttachment"]] = relationship(
        back_populates="entry", cascade="all, delete-orphan", order_by="PracticeAttachment.id"
    )


class PracticeAttachment(Base):
    __tablename__ = "practice_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(
        ForeignKey("practice_entries.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(12))
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    byte_count: Mapped[int] = mapped_column(Integer)
    data: Mapped[bytes] = mapped_column(LargeBinary)

    entry: Mapped[PracticeEntry] = relationship(back_populates="attachments")
