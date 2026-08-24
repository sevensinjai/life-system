"""Asking a constellation to befriend you, and what it does about it.

A constellation issues trials to its friends and to nobody else, so this is
the only door into the pantheon. The shape of it:

1. You ask. Optionally you say something for yourself.
2. It decides whether to hear you at all. Today that decision is a roll —
   `settings.friendship_accept_rate`, 30% by default. See **The arbiter**.
3. If it hears you, it sets a trial: an ordinary side quest, addressed to you
   rather than broadcast, from `content/challenges.py`.
4. Clear the trial and you are friends. Fail it, decline it, or let it lapse
   and the request closes.
5. Either ending — refused at the door, or refused by the trial — starts the
   same wait (`settings.friendship_retry_days`, seven days) before you may ask
   that constellation again.

**The arbiter.** Step 2 is deliberately one function behind a protocol. The
chance-based one here is a placeholder for something that reads the request:
the player's history, their standing, what they wrote, what the constellation
cares about. Everything such an arbiter would want is already on the
`Petition` it receives, and everything it might want to say back has a home in
`verdict_reason`, so replacing it means writing one callable — not touching
this flow.
"""

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.content.challenges import challenge_for
from app.errors import ValidationError
from app.models import (
    Constellation,
    ConstellationFavor,
    EventType,
    FriendshipRequest,
    FriendshipStatus,
    Player,
    SideQuest,
    SideQuestOffer,
    SideQuestOfferStatus,
    Standing,
)
from app.services import clock, constellations, story
from app.services.progression import log_event

MAX_MESSAGE_LENGTH = 1000


@dataclass(frozen=True)
class Petition:
    """Everything the constellation knows when it decides whether to hear you.

    Assembled for the arbiter, and deliberately more than the chance-based one
    needs — it is the argument list a reading arbiter will want, fixed now so
    that swapping one in changes no call sites.
    """

    player: Player
    constellation: Constellation
    favor: ConstellationFavor
    standing: Standing
    message: str | None
    previous_requests: int
    now: datetime


@dataclass(frozen=True)
class Verdict:
    """The constellation's answer to being asked."""

    heard: bool
    reason: str | None = None


class Arbiter(Protocol):
    """Whatever decides if a request is heard."""

    def __call__(self, petition: Petition) -> Verdict: ...


@dataclass
class ChanceArbiter:
    """Hears a fixed share of requests, and reads nothing.

    A placeholder with the manners of a real one: it takes the whole petition
    and returns a reason, so the day something reads the request, only this
    class is replaced.

    The generator is injectable so tests can pin the outcome — the flow around
    it is exact, and only this one step is meant to be uncertain.
    """

    rate: float
    rng: random.Random | None = None

    def __call__(self, petition: Petition) -> Verdict:
        rng = self.rng or random
        if rng.random() < self.rate:
            return Verdict(heard=True, reason="The request was heard.")
        return Verdict(heard=False, reason="The request was not heard this time.")


def default_arbiter(settings: Settings) -> Arbiter:
    """The arbiter the app runs with unless a caller passes its own."""
    return ChanceArbiter(rate=settings.friendship_accept_rate)


# --------------------------------------------------------------------------
# Reading the state of a friendship
# --------------------------------------------------------------------------


def is_friend(
    db: Session, player: Player, constellation: Constellation | None
) -> bool:
    """Whether this constellation issues to this player.

    A broadcast with nobody behind it has no friendship to check — the System
    itself reaches everyone who opted in.
    """
    if constellation is None:
        return True
    return constellations.get_favor(db, player, constellation).is_friend


def latest_request(
    db: Session, player: Player, constellation: Constellation
) -> FriendshipRequest | None:
    """The most recent time this player asked this constellation."""
    return db.scalar(
        select(FriendshipRequest)
        .where(
            FriendshipRequest.player_id == player.id,
            FriendshipRequest.constellation_id == constellation.id,
        )
        .order_by(FriendshipRequest.requested_at.desc(), FriendshipRequest.id.desc())
    )


def open_request(
    db: Session, player: Player, constellation: Constellation
) -> FriendshipRequest | None:
    """The request still awaiting a trial's outcome, if there is one."""
    latest = latest_request(db, player, constellation)
    if latest is not None and latest.status is FriendshipStatus.CHALLENGED:
        return latest
    return None


def may_ask(
    db: Session, player: Player, constellation: Constellation, now: datetime
) -> tuple[bool, str | None]:
    """Whether a request would be accepted for consideration, and why not.

    Returned as a reason rather than raised, so a client can render a disabled
    button with the right label instead of discovering the answer by asking.
    """
    favor = constellations.get_favor(db, player, constellation)
    if favor.is_friend:
        return False, "already_friends"

    if not constellation.is_active:
        return False, "retired"

    if open_request(db, player, constellation) is not None:
        return False, "request_open"

    if favor.may_ask_after is not None and clock.as_utc(
        favor.may_ask_after
    ) > clock.as_utc(now):
        return False, "too_soon"

    return True, None


def retry_at(
    db: Session, player: Player, constellation: Constellation
) -> datetime | None:
    """When this player may next ask, if they are waiting."""
    if open_request(db, player, constellation) is not None:
        return None
    return constellations.get_favor(db, player, constellation).may_ask_after


# --------------------------------------------------------------------------
# Asking
# --------------------------------------------------------------------------


def request_friendship(
    db: Session,
    player: Player,
    constellation: Constellation,
    settings: Settings,
    *,
    message: str | None = None,
    arbiter: Arbiter | None = None,
    now: datetime | None = None,
) -> FriendshipRequest:
    """Ask a constellation to befriend you, and get its answer at once.

    Comes back either REFUSED — with `retry_after` set — or CHALLENGED, with a
    trial waiting in the player's side quests. Both are answers; neither is an
    error.
    """
    now = now or clock.utcnow()
    arbiter = arbiter or default_arbiter(settings)

    allowed, reason = may_ask(db, player, constellation, now)
    if not allowed:
        raise ValidationError(_refusal_to_hear(reason, db, player, constellation))

    message = (message or "").strip() or None
    if message is not None and len(message) > MAX_MESSAGE_LENGTH:
        raise ValidationError(
            f"A request may be at most {MAX_MESSAGE_LENGTH} characters."
        )

    favor = constellations.get_favor(db, player, constellation)
    petition = Petition(
        player=player,
        constellation=constellation,
        favor=favor,
        standing=story.standing_for(favor.favor),
        message=message,
        previous_requests=_previous_request_count(db, player, constellation),
        now=now,
    )
    verdict = arbiter(petition)

    request = FriendshipRequest(
        constellation_id=constellation.id,
        player_id=player.id,
        message=message,
        verdict_reason=verdict.reason,
        requested_at=now,
        decided_at=now,
    )
    db.add(request)

    if not verdict.heard:
        _refuse(db, player, constellation, request, settings, now)
        return request

    _challenge(db, player, constellation, request, now)
    return request


def _previous_request_count(
    db: Session, player: Player, constellation: Constellation
) -> int:
    return len(
        db.scalars(
            select(FriendshipRequest.id).where(
                FriendshipRequest.player_id == player.id,
                FriendshipRequest.constellation_id == constellation.id,
            )
        ).all()
    )


def _refusal_to_hear(
    reason: str | None, db: Session, player: Player, constellation: Constellation
) -> str:
    """The 422 message for a request that cannot even be put."""
    match reason:
        case "already_friends":
            return f"{constellation.code_name} is already your friend."
        case "request_open":
            return (
                f"{constellation.code_name} has already set you a trial. "
                "Finish it before asking again."
            )
        case "too_soon":
            when = retry_at(db, player, constellation)
            return (
                f"{constellation.code_name} will not hear you again yet"
                + (f"; try after {clock.as_utc(when).isoformat()}." if when else ".")
            )
        case "retired":
            return f"{constellation.code_name} no longer answers."
        case _:
            return f"{constellation.code_name} will not hear you."


def _refuse(
    db: Session,
    player: Player,
    constellation: Constellation,
    request: FriendshipRequest,
    settings: Settings,
    now: datetime,
) -> None:
    """Turn a request away at the door, and start the wait."""
    request.status = FriendshipStatus.REFUSED
    request.resolved_at = now
    # A refusal is a meeting, so it leaves a favor row behind — the wait has
    # to be recorded somewhere, and this is the pair's row.
    favor = constellations.ensure_favor(db, player, constellation)
    favor.may_ask_after = now + timedelta(days=settings.friendship_retry_days)
    db.flush()

    standing = constellations.standing_of(db, player, constellation)
    line = story.pick_line(
        "refuse",
        standing,
        voice=constellation.voice,
        fallback=_system_voice(),
        seed=request.id,
    )

    log_event(
        db,
        player,
        EventType.FRIENDSHIP_REFUSED,
        f"{constellation.code_name}: {line}" if line else f"{constellation.code_name} said no.",
        {
            "constellation": constellation.code,
            "constellation_name": constellation.code_name,
            "request_id": request.id,
            "line": line,
            "retry_after": favor.may_ask_after.isoformat(),
        },
    )


def _challenge(
    db: Session,
    player: Player,
    constellation: Constellation,
    request: FriendshipRequest,
    now: datetime,
) -> None:
    """Set the trial of admission, addressed to this player alone."""
    from app.services.side_quests import create_side_quest, make_offer

    entry = challenge_for(constellation.code)
    if entry is None:
        raise ValidationError(
            f"{constellation.code_name} has no trial of admission written for it."
        )

    from app.content.broadcasts import as_lines_payload

    side_quest = create_side_quest(
        db,
        title=entry.title,
        description=entry.description,
        constellation=constellation,
        catalog_code=entry.code,
        lines=as_lines_payload(entry),
        difficulty=entry.difficulty,
        target_count=entry.target_count,
        unit=entry.unit,
        exp_reward=entry.exp_reward,
        stat_reward=entry.stat_reward,
        stat_reward_amount=entry.stat_reward_amount,
        penalty_exp=entry.penalty_exp,
        broadcast_at=now,
        expires_at=now + timedelta(hours=entry.window_hours),
        is_challenge=True,
        now=now,
    )

    # A trial nobody asked for would be an interruption; this one was asked
    # for, so it is handed over directly rather than going through dispatch —
    # and it ignores the weekly cap, which rations interruptions.
    preference = _preference_of(db, player)
    offer = make_offer(db, side_quest, player, preference, now=now)

    request.status = FriendshipStatus.CHALLENGED
    request.challenge_offer_id = offer.id
    db.flush()


def _preference_of(db: Session, player: Player):
    from app.services.side_quests import get_preference

    return get_preference(db, player)


def _system_voice() -> dict:
    from app.content.pantheon import SYSTEM_VOICE

    return SYSTEM_VOICE


# --------------------------------------------------------------------------
# Settling the trial
# --------------------------------------------------------------------------


def settle_challenge(
    db: Session,
    player: Player,
    offer: SideQuestOffer,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> FriendshipRequest | None:
    """Resolve the request a settled challenge belongs to.

    Called from the side quest lifecycle at every ending, and a no-op for an
    ordinary trial — which is what keeps the two flows from having to know
    much about each other.
    """
    now = now or clock.utcnow()

    request = db.scalar(
        select(FriendshipRequest).where(
            FriendshipRequest.challenge_offer_id == offer.id,
            FriendshipRequest.status == FriendshipStatus.CHALLENGED,
        )
    )
    if request is None:
        return None

    side_quest = db.get(SideQuest, offer.side_quest_id)
    constellation = side_quest.constellation if side_quest else None
    if constellation is None:
        return None

    if offer.status is SideQuestOfferStatus.COMPLETED:
        _befriend(db, player, constellation, request, now)
        return request

    if offer.status is SideQuestOfferStatus.WITHDRAWN:
        # The trial was called off. Not the player's doing, so no wait.
        request.status = FriendshipStatus.WITHDRAWN
        request.resolved_at = now
        db.flush()
        return request

    _rebuff(db, player, constellation, request, settings, now)
    return request


def _befriend(
    db: Session,
    player: Player,
    constellation: Constellation,
    request: FriendshipRequest,
    now: datetime,
) -> None:
    """The trial was cleared. Open the channel."""
    favor = constellations.ensure_favor(db, player, constellation)
    favor.is_friend = True
    favor.befriended_at = now
    favor.unfriended_at = None
    favor.may_ask_after = None

    request.status = FriendshipStatus.ACCEPTED
    request.resolved_at = now
    db.flush()

    standing = story.standing_for(favor.favor)
    line = story.pick_line(
        "befriend",
        standing,
        voice=constellation.voice,
        fallback=_system_voice(),
        seed=request.id,
    )

    log_event(
        db,
        player,
        EventType.FRIENDSHIP_FORMED,
        f"{constellation.code_name}: {line}"
        if line
        else f"{constellation.code_name} calls you a friend.",
        {
            "constellation": constellation.code,
            "constellation_name": constellation.code_name,
            "request_id": request.id,
            "line": line,
            "standing": standing.value,
        },
    )


def _rebuff(
    db: Session,
    player: Player,
    constellation: Constellation,
    request: FriendshipRequest,
    settings: Settings,
    now: datetime,
) -> None:
    """The trial went unfinished. Close the request and start the wait."""
    request.status = FriendshipStatus.FAILED
    request.resolved_at = now
    favor = constellations.ensure_favor(db, player, constellation)
    favor.may_ask_after = now + timedelta(days=settings.friendship_retry_days)
    db.flush()

    standing = constellations.standing_of(db, player, constellation)
    line = story.pick_line(
        "rebuff",
        standing,
        voice=constellation.voice,
        fallback=_system_voice(),
        seed=request.id,
    )

    log_event(
        db,
        player,
        EventType.FRIENDSHIP_FAILED,
        f"{constellation.code_name}: {line}"
        if line
        else f"{constellation.code_name} closed your request.",
        {
            "constellation": constellation.code,
            "constellation_name": constellation.code_name,
            "request_id": request.id,
            "line": line,
            "retry_after": favor.may_ask_after.isoformat(),
        },
    )


# --------------------------------------------------------------------------
# Ending it
# --------------------------------------------------------------------------


def end_friendship(
    db: Session,
    player: Player,
    constellation: Constellation,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> ConstellationFavor:
    """Walk away from a constellation.

    Its trials stop reaching you. Favor is left exactly where it stood — the
    history happened, and walking away is not itself a betrayal — but asking
    to come back waits out the same period a refusal does, so a friendship is
    not something to flip on and off.

    Anything already accepted stays yours to finish, for the same reason the
    System does not retract a quest you took up.
    """
    now = now or clock.utcnow()

    favor = constellations.get_favor(db, player, constellation)
    if not favor.is_friend:
        raise ValidationError(f"{constellation.code_name} is not your friend.")

    favor = constellations.ensure_favor(db, player, constellation)
    favor.is_friend = False
    favor.unfriended_at = now
    favor.may_ask_after = now + timedelta(days=settings.friendship_retry_days)
    db.flush()

    standing = story.standing_for(favor.favor)
    line = story.pick_line(
        "farewell",
        standing,
        voice=constellation.voice,
        fallback=_system_voice(),
        seed=favor.id or 0,
    )

    log_event(
        db,
        player,
        EventType.FRIENDSHIP_ENDED,
        f"{constellation.code_name}: {line}"
        if line
        else f"You are no longer a friend of {constellation.code_name}.",
        {
            "constellation": constellation.code,
            "constellation_name": constellation.code_name,
            "line": line,
            "standing": standing.value,
        },
    )
    return favor


def friends_of(db: Session, player: Player) -> list[Constellation]:
    """Every constellation that currently issues to this player."""
    return list(
        db.scalars(
            select(Constellation)
            .join(
                ConstellationFavor,
                ConstellationFavor.constellation_id == Constellation.id,
            )
            .where(
                ConstellationFavor.player_id == player.id,
                ConstellationFavor.is_friend.is_(True),
            )
            .order_by(Constellation.id)
        )
    )
