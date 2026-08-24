"""The pantheon: who issues side quests, and what they make of each player.

A side quest arrives from somebody. `Constellation` is that somebody — a
named thing with a domain it cares about and a voice it speaks in. The cast is
small and fixed, written by hand in `app/content/pantheon.py` and seeded into
this table, so a constellation is a row a broadcast can point at rather than a
string typed into each one.

`ConstellationFavor` is the other half: what one constellation makes of one
player. Clearing its quests raises favor, dropping them lowers it, and the
band that favor falls into — the player's *standing* — decides how it talks to
you and what it will send. It also carries whether the two are *friends*,
which is what opens the channel in the first place: a constellation issues
trials to its friends and to nobody else.

`FriendshipRequest` is how that channel gets opened. You ask; the
constellation may decline to hear you, or set you a trial; clearing the trial
makes you friends. Every request is kept, refusals included, because the
history is the story of how you got in — and because an arbiter that actually
reads the request, rather than rolling for it, will want that history.

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
from app.models.enums import FriendshipStatus, MythTradition, StatName

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.side_quest import SideQuest, SideQuestOffer


class Constellation(Base):
    """One of the things watching. The author of a side quest."""

    __tablename__ = "constellations"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable slug the catalog and the seed script agree on, e.g. "xingtian".
    # Not a name — an identifier. Names get rewritten; this survives the edit.
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    # Two names, because a constellation has two.
    #
    # The **code name** is what it is called: a title, grand and impersonal,
    # the thing that appears when it speaks. The **real name** is who it was
    # before it was a constellation — a person's name, which is the point of
    # having one at all.
    #
    # Both are carried in English and Traditional Chinese. Names are the one
    # part of this content that is bilingual today: the voices and the trials
    # are still English-only until the localization pass, but a name is
    # identity rather than prose, and a client may reasonably want to show
    # both at once — 「猛志常在」 The Will That Remains — rather than pick one.
    # Which body of myth it comes out of. Stored rather than derived because
    # a pantheon this size is read grouped, not as one list.
    tradition: Mapped[MythTradition] = mapped_column(
        Enum(MythTradition, native_enum=False, length=16),
        default=MythTradition.GREEK,
        index=True,
    )

    code_name: Mapped[str] = mapped_column(String(120))
    code_name_zh_hant: Mapped[str | None] = mapped_column(String(120), nullable=True)
    real_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    real_name_zh_hant: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # The line under the name — "who fell, and stood up anyway".
    epithet: Mapped[str | None] = mapped_column(String(200), nullable=True)
    epithet_zh_hant: Mapped[str | None] = mapped_column(String(200), nullable=True)
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
        return f"<Constellation code={self.code!r} name={self.code_name!r}>"


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

    # Whether this constellation issues to this player at all. False until a
    # request is granted and its trial cleared; false again if either side
    # walks away.
    is_friend: Mapped[bool] = mapped_column(Boolean, default=False)
    befriended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    unfriended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # The earliest this player may ask this constellation again. Set by a
    # refusal, by a failed trial of admission, and by walking away. It lives
    # on the pair rather than on any one request because that is what it is
    # about: these two, and how soon they may speak again.
    may_ask_after: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
            f"player_id={self.player_id} favor={self.favor} "
            f"friend={self.is_friend}>"
        )


class FriendshipRequest(Base):
    """One attempt to befriend one constellation.

    A log, kept whatever the outcome: a refusal is as much a part of the
    record as an acceptance, and it is what a later arbiter reading the
    history will want to see. The wait a refusal imposes is not here — that
    belongs to the pair, on `ConstellationFavor.may_ask_after`.
    """

    __tablename__ = "friendship_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    constellation_id: Mapped[int] = mapped_column(
        ForeignKey("constellations.id", ondelete="CASCADE"), index=True
    )
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )

    status: Mapped[FriendshipStatus] = mapped_column(
        Enum(FriendshipStatus, native_enum=False, length=16),
        default=FriendshipStatus.CHALLENGED,
        index=True,
    )

    # What the player said for themselves, if anything. Nothing reads it yet;
    # it is here because an arbiter that weighs a request rather than rolling
    # for it needs something to weigh.
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Why it went the way it did, in words. A stock line today.
    verdict_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # The trial that was set, if one was. A side quest like any other, which
    # is why it is an offer rather than a shape of its own.
    challenge_offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("side_quest_offers.id", ondelete="SET NULL"), nullable=True
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    # When the constellation answered the request, and when the trial it set
    # was settled. The same instant for a refusal, which needs no trial.
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    constellation: Mapped["Constellation"] = relationship()
    player: Mapped["Player"] = relationship(back_populates="friendship_requests")
    challenge_offer: Mapped["SideQuestOffer | None"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<FriendshipRequest constellation_id={self.constellation_id} "
            f"player_id={self.player_id} status={self.status}>"
        )
