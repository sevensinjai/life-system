"""Quests, their per-day instances, and the penalties failure incurs."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import QuestDifficulty, QuestStatus, QuestType, StatName

if TYPE_CHECKING:
    from app.models.player import Player


class Quest(Base):
    """A quest definition.

    A daily quest is a template: it spawns one QuestInstance per day. A normal
    quest is one-shot and owns exactly one instance.
    """

    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    quest_type: Mapped[QuestType] = mapped_column(
        Enum(QuestType, native_enum=False, length=16), default=QuestType.NORMAL
    )
    difficulty: Mapped[QuestDifficulty] = mapped_column(
        Enum(QuestDifficulty, native_enum=False, length=2), default=QuestDifficulty.E
    )

    # How many units clear the quest, e.g. 100 push-ups.
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)

    exp_reward: Mapped[int] = mapped_column(Integer)
    stat_reward: Mapped[StatName | None] = mapped_column(
        Enum(StatName, native_enum=False, length=16), nullable=True
    )
    stat_reward_amount: Mapped[int] = mapped_column(Integer, default=0)

    # Archived quests stop spawning instances but keep their history.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    player: Mapped["Player"] = relationship(back_populates="quests")
    instances: Mapped[list["QuestInstance"]] = relationship(
        back_populates="quest", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Quest id={self.id} title={self.title!r} type={self.quest_type}>"


class QuestInstance(Base):
    """One attempt at a quest on one day."""

    __tablename__ = "quest_instances"
    __table_args__ = (
        # Makes the daily reset idempotent: re-running it cannot duplicate a day.
        UniqueConstraint("quest_id", "quest_date", name="uq_quest_instance_per_day"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quest_id: Mapped[int] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), index=True
    )
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    # The player's local date this instance belongs to.
    quest_date: Mapped[date] = mapped_column(Date, index=True)

    progress: Mapped[int] = mapped_column(Integer, default=0)
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[QuestStatus] = mapped_column(
        Enum(QuestStatus, native_enum=False, length=16), default=QuestStatus.ACTIVE
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    quest: Mapped["Quest"] = relationship(back_populates="instances")

    @property
    def is_cleared(self) -> bool:
        return self.progress >= self.target_count

    def __repr__(self) -> str:
        return (
            f"<QuestInstance id={self.id} quest_id={self.quest_id} "
            f"date={self.quest_date} status={self.status}>"
        )


class Penalty(Base):
    """EXP docked for letting a daily quest expire unfinished."""

    __tablename__ = "penalties"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )
    quest_instance_id: Mapped[int | None] = mapped_column(
        ForeignKey("quest_instances.id", ondelete="SET NULL"), nullable=True
    )

    reason: Mapped[str] = mapped_column(String(255))
    exp_lost: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    player: Mapped["Player"] = relationship(back_populates="penalties")

    def __repr__(self) -> str:
        return f"<Penalty id={self.id} exp_lost={self.exp_lost}>"
