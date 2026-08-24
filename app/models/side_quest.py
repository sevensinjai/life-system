"""System-wide side quests: what the sky announces, and who took it up.

A quest is authored by a player, for that player. A **side quest** is not: it
is issued by the System itself — a constellation, a god, whatever the story
settles on later — and goes out to every opted-in player at once. Three tables
carry that:

* ``SideQuest`` — the broadcast. One row, shared by everyone.
* ``SideQuestOffer`` — one row per player the broadcast reached, holding their
  answer and their progress. The per-player half of a global event.
* ``SideQuestPreference`` — whether a player wants to be reached at all, and
  how often. No row means opted out: nobody is enrolled by default.

Two deliberate differences from quests:

**Side quests run on absolute UTC instants, not player-local dates.** A
broadcast reaches Seoul and São Paulo at the same moment, so its window cannot
be a calendar day the way a daily quest's is.

**Ignoring one is free.** Only an offer that was *accepted* and then left
unfinished can cost EXP, and only if the broadcast carried a penalty at all.
Declining, never answering, and having the quest withdrawn are all recorded
separately and all cost nothing — an optional system that punishes you for
opting in is not optional.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
from app.models.enums import (
    QuestDifficulty,
    SideQuestFrequency,
    SideQuestOfferStatus,
    SideQuestStatus,
    StatName,
)
from app.services.clock import as_utc

if TYPE_CHECKING:
    from app.models.player import Player


class SideQuest(Base):
    """A broadcast: one quest the System puts to everybody at once.

    It carries the same reward shape as a quest — EXP, an optional stat, a
    difficulty rank — plus the things only a global event needs: when it goes
    out, when it closes, and who it is meant for.
    """

    __tablename__ = "side_quests"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Who is speaking — the constellation, god, or whatever issued this. Free
    # text for now; the story layer will decide what these actually are.
    herald: Mapped[str | None] = mapped_column(String(120), nullable=True)

    difficulty: Mapped[QuestDifficulty] = mapped_column(
        Enum(QuestDifficulty, native_enum=False, length=2), default=QuestDifficulty.E
    )

    target_count: Mapped[int] = mapped_column(Integer, default=1)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)

    exp_reward: Mapped[int] = mapped_column(Integer)
    stat_reward: Mapped[StatName | None] = mapped_column(
        Enum(StatName, native_enum=False, length=16), nullable=True
    )
    stat_reward_amount: Mapped[int] = mapped_column(Integer, default=0)
    # EXP charged for accepting and then not finishing. Zero — the default —
    # makes the whole broadcast risk-free; a harsher patron can set it.
    penalty_exp: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[SideQuestStatus] = mapped_column(
        Enum(SideQuestStatus, native_enum=False, length=16),
        default=SideQuestStatus.DRAFT,
        index=True,
    )

    # Both in UTC: a broadcast is a moment, the same one for every player.
    broadcast_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True
    )
    # Null means the offer waits indefinitely, as a one-time quest does.
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # Audience bounds, so an S-rank trial can skip level 2 players outright.
    min_level: Mapped[int] = mapped_column(Integer, default=1)
    max_level: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    offers: Mapped[list["SideQuestOffer"]] = relationship(
        back_populates="side_quest", cascade="all, delete-orphan"
    )

    def is_open(self, now: datetime) -> bool:
        """Whether the broadcast is out and still taking progress."""
        if self.status is not SideQuestStatus.BROADCAST:
            return False
        return self.expires_at is None or as_utc(self.expires_at) > as_utc(now)

    def has_lapsed(self, now: datetime) -> bool:
        """Whether the window closed. A broadcast with no deadline never does."""
        if self.expires_at is None:
            return False
        return as_utc(self.expires_at) <= as_utc(now)

    def covers_level(self, level: int) -> bool:
        """Whether a player at this level is in the intended audience."""
        if level < self.min_level:
            return False
        return self.max_level is None or level <= self.max_level

    def __repr__(self) -> str:
        return f"<SideQuest id={self.id} title={self.title!r} status={self.status}>"


class SideQuestOffer(Base):
    """One player's copy of a broadcast: their answer, and their progress."""

    __tablename__ = "side_quest_offers"
    __table_args__ = (
        # Makes dispatch idempotent: re-running a broadcast cannot offer the
        # same side quest to the same player twice.
        UniqueConstraint(
            "side_quest_id", "player_id", name="uq_side_quest_offer_per_player"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    side_quest_id: Mapped[int] = mapped_column(
        ForeignKey("side_quests.id", ondelete="CASCADE"), index=True
    )
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    status: Mapped[SideQuestOfferStatus] = mapped_column(
        Enum(SideQuestOfferStatus, native_enum=False, length=16),
        default=SideQuestOfferStatus.OFFERED,
        index=True,
    )

    progress: Mapped[int] = mapped_column(Integer, default=0)
    # Snapshotted at dispatch, as a quest instance snapshots its target, so
    # retuning a broadcast mid-flight cannot move the goalposts on someone.
    target_count: Mapped[int] = mapped_column(Integer, default=1)
    # Also snapshotted: the sweep that lapses offers can then run off this
    # table alone, without joining every broadcast to find the deadline.
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    offered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    # When the player accepted or declined. Null while still unanswered.
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    side_quest: Mapped["SideQuest"] = relationship(back_populates="offers")
    player: Mapped["Player"] = relationship(back_populates="side_quest_offers")

    @property
    def is_cleared(self) -> bool:
        return self.progress >= self.target_count

    @property
    def is_live(self) -> bool:
        """Whether this offer still wants something from the player."""
        return self.status in (
            SideQuestOfferStatus.OFFERED,
            SideQuestOfferStatus.ACCEPTED,
        )

    def has_lapsed(self, now: datetime) -> bool:
        """Whether the window closed. An offer with no deadline never does."""
        if self.expires_at is None:
            return False
        return as_utc(self.expires_at) <= as_utc(now)

    def __repr__(self) -> str:
        return (
            f"<SideQuestOffer id={self.id} side_quest_id={self.side_quest_id} "
            f"player_id={self.player_id} status={self.status}>"
        )


class SideQuestPreference(Base):
    """A player's standing answer to "do you want side quests at all?".

    One row per player, written the first time they choose. No row means opted
    out, which is why registration does not create one — being enrolled has to
    be something you did, not something that happened to you.
    """

    __tablename__ = "side_quest_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), unique=True, index=True
    )

    is_opted_in: Mapped[bool] = mapped_column(Boolean, default=False)
    frequency: Mapped[SideQuestFrequency] = mapped_column(
        Enum(SideQuestFrequency, native_enum=False, length=16),
        default=SideQuestFrequency.OCCASIONAL,
    )
    # The hardest rank the player is willing to be sent. Null accepts any.
    max_difficulty: Mapped[QuestDifficulty | None] = mapped_column(
        Enum(QuestDifficulty, native_enum=False, length=2), nullable=True
    )
    # True means "count me in without asking" — offers arrive already accepted,
    # penalty and all. False leaves every broadcast a yes/no question.
    auto_accept: Mapped[bool] = mapped_column(Boolean, default=False)

    # Kept as history rather than derived from is_opted_in, so the System can
    # tell a player who has never listened from one who stopped.
    opted_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    opted_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    player: Mapped["Player"] = relationship(back_populates="side_quest_preference")

    def __repr__(self) -> str:
        return (
            f"<SideQuestPreference player_id={self.player_id} "
            f"opted_in={self.is_opted_in} frequency={self.frequency}>"
        )
