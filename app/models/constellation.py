"""The pantheon: who issues side quests, and what they make of each player.

A side quest arrives from somebody. `Constellation` is that somebody — a
named thing with a domain it cares about and a voice it speaks in. The cast is
small and fixed, written by hand in `app/content/pantheon.py` and seeded into
this table, so a constellation is a row a broadcast can point at rather than a
string typed into each one.

`ConstellationFavor` is the other half: what one constellation makes of one
player. Clearing its quests raises favor, dropping them lowers it, and the
band that favor falls into — the player's *standing* — decides how it talks to
you and what it will send.

Standing never touches EXP, levels, or stats. A constellation can lose
interest in you; it cannot punish you. Only a side quest you accepted and
then abandoned costs anything, and that is the broadcast's penalty, not the
constellation's opinion.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
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
from app.models.enums import StatName

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.side_quest import SideQuest


class Constellation(Base):
    """One of the things watching. The author of a side quest."""

    __tablename__ = "constellations"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable slug the catalog and the seed script agree on, e.g. "fallen_star".
    # Names and voices get rewritten; this is what survives an edit.
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    name: Mapped[str] = mapped_column(String(120))
    # The line under the name — "who fell, and stood up anyway".
    epithet: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # What it cares about. Null for one that cares about the habit itself
    # rather than any one stat.
    domain: Mapped[StatName | None] = mapped_column(
        Enum(StatName, native_enum=False, length=16), nullable=True
    )

    # How it speaks: {line kind: {standing or "default": [lines]}}. Held as
    # data rather than as code so the whole voice can be swapped — for a
    # rewrite now, and for another language later.
    voice: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # A retired constellation keeps its history and its favor rows, but issues
    # nothing further.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    side_quests: Mapped[list["SideQuest"]] = relationship(
        back_populates="constellation"
    )
    favor: Mapped[list["ConstellationFavor"]] = relationship(
        back_populates="constellation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Constellation code={self.code!r} name={self.name!r}>"


class ConstellationFavor(Base):
    """What one constellation makes of one player.

    Written the first time a constellation and a player meet — which is when
    it offers them something — so a missing row means "these two have no
    history", the same way a missing preference row means "never opted in".
    """

    __tablename__ = "constellation_favor"
    __table_args__ = (
        UniqueConstraint(
            "constellation_id", "player_id", name="uq_favor_per_player"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    constellation_id: Mapped[int] = mapped_column(
        ForeignKey("constellations.id", ondelete="CASCADE"), index=True
    )
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    # The running score. Its band is derived, not stored, so retuning the
    # thresholds re-reads every player's standing instead of migrating it.
    favor: Mapped[int] = mapped_column(Integer, default=0)

    # The history behind the number, kept because a screen wants to say "three
    # cleared, one abandoned" rather than "favor 14".
    offers_received: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[int] = mapped_column(Integer, default=0)
    declined: Mapped[int] = mapped_column(Integer, default=0)
    expired: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)

    first_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    constellation: Mapped["Constellation"] = relationship(back_populates="favor")
    player: Mapped["Player"] = relationship(back_populates="constellation_favor")

    def __repr__(self) -> str:
        return (
            f"<ConstellationFavor constellation_id={self.constellation_id} "
            f"player_id={self.player_id} favor={self.favor}>"
        )
