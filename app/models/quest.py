"""Quests, their per-day instances, and the penalties failure incurs."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
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
from app.models.enums import QuestDifficulty, QuestStatus, ScheduleKind, StatName

if TYPE_CHECKING:
    from app.models.player import Player


class Quest(Base):
    """A quest definition, authored by the player.

    A recurring quest is a template: it spawns one QuestInstance per period,
    where the schedule decides how long a period is and when it opens. A
    one-time quest owns a single instance whose period never ends.
    """

    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    schedule: Mapped[ScheduleKind] = mapped_column(
        Enum(ScheduleKind, native_enum=False, length=16), default=ScheduleKind.ONCE
    )
    # Weekdays a WEEKDAYS quest falls on: 0 = Monday .. 6 = Sunday.
    schedule_days: Mapped[list[int] | None] = mapped_column(JSON, nullable=True)
    # Period length for an INTERVAL quest.
    schedule_interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # The day the recurrence counts from; also the first period's start.
    schedule_anchor: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Which weekday a WEEKLY period opens on.
    week_start: Mapped[int] = mapped_column(Integer, default=0)

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

    # Clearing the quest trains this skill. Null keeps the quest purely about
    # player EXP. SET NULL rather than CASCADE: deleting a skill should not
    # take the quests that referenced it with it.
    skill_id: Mapped[int | None] = mapped_column(
        ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True
    )
    skill_exp_reward: Mapped[int] = mapped_column(Integer, default=0)

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
        return f"<Quest id={self.id} title={self.title!r} schedule={self.schedule}>"


class QuestInstance(Base):
    """One attempt at a quest, covering one period."""

    __tablename__ = "quest_instances"
    __table_args__ = (
        # Makes the reset idempotent: re-running it cannot duplicate a period.
        UniqueConstraint(
            "quest_id", "period_start", name="uq_quest_instance_per_period"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quest_id: Mapped[int] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), index=True
    )
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    # The player-local window this instance is open for. A null end never
    # lapses, which is how one-time quests wait indefinitely.
    period_start: Mapped[date] = mapped_column(Date, index=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)

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

    def covers(self, day: date) -> bool:
        """Whether this instance is the one open on `day`."""
        if day < self.period_start:
            return False
        return self.period_end is None or day <= self.period_end

    def has_lapsed(self, today: date) -> bool:
        """Whether the window closed before `today`."""
        return self.period_end is not None and self.period_end < today

    def __repr__(self) -> str:
        return (
            f"<QuestInstance id={self.id} quest_id={self.quest_id} "
            f"period={self.period_start}..{self.period_end} status={self.status}>"
        )


class Penalty(Base):
    """EXP docked for letting a quest — or an accepted side quest — lapse."""

    __tablename__ = "penalties"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )
    # Exactly one of these points at the thing that lapsed; both are null once
    # that row is gone, leaving `reason` as the record.
    quest_instance_id: Mapped[int | None] = mapped_column(
        ForeignKey("quest_instances.id", ondelete="SET NULL"), nullable=True
    )
    side_quest_offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("side_quest_offers.id", ondelete="SET NULL"), nullable=True
    )

    reason: Mapped[str] = mapped_column(String(255))
    exp_lost: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    player: Mapped["Player"] = relationship(back_populates="penalties")

    def __repr__(self) -> str:
        return f"<Penalty id={self.id} exp_lost={self.exp_lost}>"
