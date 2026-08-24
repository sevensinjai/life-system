"""The player's System profile: level, EXP, and stats."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import StatName

if TYPE_CHECKING:
    from app.models.event import SystemEvent
    from app.models.quest import Penalty, Quest
    from app.models.quote import Quote
    from app.models.side_quest import SideQuestOffer, SideQuestPreference
    from app.models.user import User


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )

    name: Mapped[str] = mapped_column(String(80))

    level: Mapped[int] = mapped_column(Integer, default=1)
    # EXP accumulated toward the NEXT level, not a lifetime total.
    exp: Mapped[int] = mapped_column(Integer, default=0)
    total_exp_earned: Mapped[int] = mapped_column(Integer, default=0)
    stat_points: Mapped[int] = mapped_column(Integer, default=0)

    strength: Mapped[int] = mapped_column(Integer, default=10)
    agility: Mapped[int] = mapped_column(Integer, default=10)
    vitality: Mapped[int] = mapped_column(Integer, default=10)
    intelligence: Mapped[int] = mapped_column(Integer, default=10)
    perception: Mapped[int] = mapped_column(Integer, default=10)

    # IANA name. Daily resets happen at midnight here, not at UTC midnight.
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="player")
    quests: Mapped[list["Quest"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    quotes: Mapped[list["Quote"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    side_quest_offers: Mapped[list["SideQuestOffer"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    # Absent until the player answers the opt-in question, which is what makes
    # "no preference" mean "not enrolled".
    side_quest_preference: Mapped["SideQuestPreference | None"] = relationship(
        back_populates="player", uselist=False, cascade="all, delete-orphan"
    )
    penalties: Mapped[list["Penalty"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    events: Mapped[list["SystemEvent"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )

    def get_stat(self, stat: StatName) -> int:
        return getattr(self, stat.value)

    def add_stat(self, stat: StatName, amount: int) -> None:
        setattr(self, stat.value, self.get_stat(stat) + amount)

    def __repr__(self) -> str:
        return f"<Player id={self.id} name={self.name!r} level={self.level}>"
