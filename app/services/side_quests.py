"""Side quests: what the System broadcasts, and who chose to hear it.

The shape of the feature in one paragraph. The System — a constellation, a
god, the story layer will say — issues a quest to everybody at once. It only
reaches players who opted in, and only as often as each of them agreed to be
interrupted. Reaching a player creates an *offer*, which they accept, decline,
or ignore. Accepting is the only branch that can ever cost EXP, and only when
the broadcast carried a penalty to begin with.

Every timestamp here is UTC. A broadcast is a single moment shared by every
player, which is why side quests do not use the player-local dates quests do.

Who issues a broadcast, what it says, and what it makes of the player's answer
are the story layer: `content/` holds the writing, `services/story.py` the
pure rules, and `services/constellations.py` the regard each constellation
keeps. This module calls into them at each ending; it does not write any of
the player-facing prose itself.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import NotFoundError, ValidationError
from app.models import (
    DIFFICULTY_EXP,
    SIDE_QUEST_OFFERS_PER_WEEK,
    Constellation,
    EventType,
    Player,
    QuestDifficulty,
    SideQuest,
    SideQuestFrequency,
    SideQuestOffer,
    SideQuestOfferStatus,
    SideQuestPreference,
    SideQuestStatus,
    Standing,
    StatName,
)
from app.services import clock, constellations, friendship, story
from app.services.progression import apply_exp_penalty, award_exp, log_event

# The trailing window a frequency cap is measured over.
FREQUENCY_WINDOW_DAYS = 7

DEFAULT_FREQUENCY = SideQuestFrequency.OCCASIONAL

MAX_TITLE_LENGTH = 200
MAX_HERALD_LENGTH = 120


class _Unset:
    """Sentinel for optional fields whose meaningful value includes None."""


UNSET = _Unset()


# --------------------------------------------------------------------------
# Preferences: the opt-in itself
# --------------------------------------------------------------------------


def default_preference(player: Player) -> SideQuestPreference:
    """The standing answer for a player who has never been asked: no.

    Transient on purpose — it is never added to the session. A player who has
    not opted in leaves no row behind, so "have you answered?" and "what did
    you answer?" stay separate questions.
    """
    return SideQuestPreference(
        player_id=player.id,
        is_opted_in=False,
        frequency=DEFAULT_FREQUENCY,
        max_difficulty=None,
        auto_accept=False,
    )


def get_preference(db: Session, player: Player) -> SideQuestPreference:
    """The player's side quest settings, real or defaulted."""
    stored = db.scalar(
        select(SideQuestPreference).where(
            SideQuestPreference.player_id == player.id
        )
    )
    return stored if stored is not None else default_preference(player)


def set_preference(
    db: Session,
    player: Player,
    *,
    is_opted_in: bool | None = None,
    frequency: SideQuestFrequency | None = None,
    max_difficulty: QuestDifficulty | None | _Unset = UNSET,
    auto_accept: bool | None = None,
    now: datetime | None = None,
) -> SideQuestPreference:
    """Record the player's answer, creating their preference row if needed.

    Omitted fields are left alone. `max_difficulty` takes a real None — "send
    me anything" — so it uses a sentinel rather than None to mean "unchanged".
    """
    now = now or clock.utcnow()

    preference = db.scalar(
        select(SideQuestPreference).where(
            SideQuestPreference.player_id == player.id
        )
    )
    if preference is None:
        preference = default_preference(player)
        db.add(preference)

    if frequency is not None:
        preference.frequency = frequency
    if not isinstance(max_difficulty, _Unset):
        preference.max_difficulty = max_difficulty
    if auto_accept is not None:
        preference.auto_accept = auto_accept

    if is_opted_in is not None and is_opted_in != preference.is_opted_in:
        preference.is_opted_in = is_opted_in
        if is_opted_in:
            preference.opted_in_at = now
        else:
            preference.opted_out_at = now

    db.flush()
    return preference


def offers_per_week(preference: SideQuestPreference) -> int:
    """How many offers this player's frequency lets through in a week."""
    return SIDE_QUEST_OFFERS_PER_WEEK[preference.frequency]


def offers_in_window(
    db: Session, player: Player, now: datetime, *, days: int = FREQUENCY_WINDOW_DAYS
) -> int:
    """How many offers this player has already received in the trailing window.

    Counts offers made, not offers accepted: declining a side quest still uses
    up a slot, because the interruption is what the player agreed to ration.

    Trials of admission are left out for that same reason — the player asked
    for that one, so it is not an interruption and must not eat their week.
    """
    since = now - timedelta(days=days)
    return db.scalar(
        select(func.count(SideQuestOffer.id))
        .join(SideQuest, SideQuest.id == SideQuestOffer.side_quest_id)
        .where(
            SideQuestOffer.player_id == player.id,
            SideQuestOffer.offered_at > since,
            SideQuest.is_challenge.is_(False),
        )
    ) or 0


def skip_reason(
    db: Session,
    side_quest: SideQuest,
    player: Player,
    preference: SideQuestPreference,
    now: datetime,
) -> str | None:
    """Why this broadcast should not reach this player, or None if it should.

    Returned as a reason rather than a bool so a dispatch can report what it
    filtered out — useful when a broadcast lands on nobody and the author
    wants to know whether it was the level range or the rank cap.
    """
    if not preference.is_opted_in:
        return "opted_out"

    # A constellation issues to its friends and to nobody else. The way in is
    # its trial of admission, which is handed over directly and never passes
    # through here.
    if not friendship.is_friend(db, player, side_quest.constellation):
        return "not_a_friend"

    if (
        preference.max_difficulty is not None
        and side_quest.difficulty.rank > preference.max_difficulty.rank
    ):
        return "above_rank_cap"

    if not side_quest.covers_level(player.level):
        return "outside_level_range"

    if side_quest.min_standing is not None:
        standing = constellations.standing_of(db, player, side_quest.constellation)
        if not story.meets_standing(standing, side_quest.min_standing):
            return "standing_too_low"

    already = db.scalar(
        select(SideQuestOffer.id).where(
            SideQuestOffer.side_quest_id == side_quest.id,
            SideQuestOffer.player_id == player.id,
        )
    )
    if already is not None:
        return "already_offered"

    if offers_in_window(db, player, now) >= offers_per_week(preference):
        return "frequency_cap"

    return None


# --------------------------------------------------------------------------
# Authoring and broadcasting
# --------------------------------------------------------------------------


def default_exp_for(difficulty: QuestDifficulty) -> int:
    """A side quest pays what a quest of the same rank pays, unless overridden."""
    return DIFFICULTY_EXP[difficulty]


def create_side_quest(
    db: Session,
    *,
    title: str,
    description: str | None = None,
    constellation: Constellation | None = None,
    catalog_code: str | None = None,
    lines: dict | None = None,
    difficulty: QuestDifficulty = QuestDifficulty.E,
    target_count: int = 1,
    unit: str | None = None,
    exp_reward: int | None = None,
    stat_reward: StatName | None = None,
    stat_reward_amount: int = 0,
    penalty_exp: int = 0,
    broadcast_at: datetime | None = None,
    expires_at: datetime | None = None,
    min_level: int = 1,
    max_level: int | None = None,
    min_standing: Standing | None = None,
    is_challenge: bool = False,
    draft: bool = False,
    now: datetime | None = None,
) -> SideQuest:
    """Write a broadcast. It goes out when `broadcast` or `dispatch_due` runs.

    Queued rather than sent, so authoring and announcing stay separate steps.
    `draft=True` parks it further back still: a draft is never picked up by
    `dispatch_due`, which is what lets the story layer write ahead.

    `is_challenge=True` marks a trial of admission — addressed to the one
    player who asked for it. It is created already BROADCAST, because there is
    nobody else to send it to, and every path that reaches all players skips
    it.
    """
    now = now or clock.utcnow()
    title = title.strip()

    if not title:
        raise ValidationError("A side quest needs a title.")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError(
            f"A title may be at most {MAX_TITLE_LENGTH} characters."
        )
    if target_count < 1:
        raise ValidationError("target_count must be at least 1.")
    if stat_reward_amount < 0:
        raise ValidationError("stat_reward_amount must be non-negative.")
    if penalty_exp < 0:
        raise ValidationError("penalty_exp must be non-negative.")
    if min_level < 1:
        raise ValidationError("min_level must be at least 1.")
    if max_level is not None and max_level < min_level:
        raise ValidationError("max_level must not be below min_level.")

    broadcast_at = broadcast_at or now
    if expires_at is not None and clock.as_utc(expires_at) <= clock.as_utc(
        broadcast_at
    ):
        raise ValidationError("expires_at must be after broadcast_at.")

    side_quest = SideQuest(
        title=title,
        description=description,
        constellation_id=constellation.id if constellation else None,
        catalog_code=catalog_code,
        lines=lines or {},
        difficulty=difficulty,
        target_count=target_count,
        unit=unit,
        exp_reward=exp_reward if exp_reward is not None else default_exp_for(difficulty),
        stat_reward=stat_reward,
        stat_reward_amount=stat_reward_amount,
        penalty_exp=penalty_exp,
        status=(
            SideQuestStatus.DRAFT
            if draft
            else SideQuestStatus.BROADCAST
            if is_challenge
            else SideQuestStatus.SCHEDULED
        ),
        broadcast_at=broadcast_at,
        expires_at=expires_at,
        min_level=min_level,
        max_level=max_level,
        min_standing=min_standing,
        is_challenge=is_challenge,
    )
    db.add(side_quest)
    db.flush()
    return side_quest


@dataclass
class BroadcastResult:
    """What one broadcast actually reached."""

    side_quest_id: int
    offered_player_ids: list[int] = field(default_factory=list)
    # reason -> how many opted-in players it filtered out.
    skipped: dict[str, int] = field(default_factory=dict)

    @property
    def offered_count(self) -> int:
        return len(self.offered_player_ids)

    @property
    def skipped_count(self) -> int:
        return sum(self.skipped.values())


def broadcast(
    db: Session, side_quest: SideQuest, *, now: datetime | None = None
) -> BroadcastResult:
    """Put a side quest to every player listening for one.

    Idempotent: an offer is unique per (side quest, player), so re-running a
    broadcast reaches only players it missed the first time — someone who
    opted in an hour late, or who was under their cap by then.
    """
    now = now or clock.utcnow()

    if side_quest.is_challenge:
        raise ValidationError(
            "This is a trial of admission, set for one player; "
            "it cannot be broadcast."
        )
    if side_quest.status is SideQuestStatus.CANCELLED:
        raise ValidationError("This side quest was cancelled; it cannot be broadcast.")
    if side_quest.status is SideQuestStatus.CLOSED:
        raise ValidationError("This side quest has closed; it cannot be broadcast.")

    result = BroadcastResult(side_quest_id=side_quest.id)

    listeners = db.execute(
        select(Player, SideQuestPreference)
        .join(SideQuestPreference, SideQuestPreference.player_id == Player.id)
        .where(SideQuestPreference.is_opted_in.is_(True))
        .order_by(Player.id)
    ).all()

    for player, preference in listeners:
        reason = skip_reason(db, side_quest, player, preference, now)
        if reason is not None:
            result.skipped[reason] = result.skipped.get(reason, 0) + 1
            continue
        make_offer(db, side_quest, player, preference, now=now)
        result.offered_player_ids.append(player.id)

    side_quest.status = SideQuestStatus.BROADCAST
    return result


def dispatch_due(db: Session, *, now: datetime | None = None) -> list[BroadcastResult]:
    """Send every scheduled broadcast whose moment has come.

    Intended for the same cron that runs the daily reset. A broadcast whose
    whole window slipped past unsent is closed rather than sent late.
    """
    now = now or clock.utcnow()

    due = db.scalars(
        select(SideQuest)
        .where(
            SideQuest.status == SideQuestStatus.SCHEDULED,
            SideQuest.broadcast_at <= now,
            SideQuest.is_challenge.is_(False),
        )
        .order_by(SideQuest.broadcast_at, SideQuest.id)
    ).all()

    results = []
    for side_quest in due:
        if side_quest.has_lapsed(now):
            side_quest.status = SideQuestStatus.CLOSED
            continue
        results.append(broadcast(db, side_quest, now=now))
    return results


def catch_up(
    db: Session, player: Player, *, now: datetime | None = None
) -> list[SideQuestOffer]:
    """Offer a player every open broadcast they have not seen yet.

    What a fresh opt-in runs, so saying yes has an effect now instead of at
    the next broadcast. Eligibility still applies, so the frequency cap holds:
    opting in during a busy week does not dump six side quests on someone.
    """
    now = now or clock.utcnow()
    preference = get_preference(db, player)
    if not preference.is_opted_in:
        return []

    open_quests = db.scalars(
        select(SideQuest)
        .where(
            SideQuest.status == SideQuestStatus.BROADCAST,
            (SideQuest.expires_at.is_(None)) | (SideQuest.expires_at > now),
            # Someone else's trial of admission is not an open broadcast.
            SideQuest.is_challenge.is_(False),
        )
        .order_by(SideQuest.broadcast_at, SideQuest.id)
    ).all()

    offers = []
    for side_quest in open_quests:
        if skip_reason(db, side_quest, player, preference, now) is not None:
            continue
        offers.append(make_offer(db, side_quest, player, preference, now=now))
    return offers


def make_offer(
    db: Session,
    side_quest: SideQuest,
    player: Player,
    preference: SideQuestPreference,
    *,
    now: datetime | None = None,
) -> SideQuestOffer:
    """Create one player's copy of a broadcast.

    A player who set `auto_accept` skips the yes/no step — the offer arrives
    already accepted, penalty and all, which is what they asked for.
    """
    now = now or clock.utcnow()
    accepted = preference.auto_accept

    offer = SideQuestOffer(
        side_quest_id=side_quest.id,
        player_id=player.id,
        status=(
            SideQuestOfferStatus.ACCEPTED
            if accepted
            else SideQuestOfferStatus.OFFERED
        ),
        progress=0,
        target_count=side_quest.target_count,
        expires_at=side_quest.expires_at,
        offered_at=now,
        responded_at=now if accepted else None,
    )
    db.add(offer)
    db.flush()

    constellations.record_offer(db, player, side_quest.constellation, now=now)
    message, told = _narrate(db, player, side_quest, story.OFFER, seed=offer.id)

    log_event(
        db,
        player,
        EventType.SIDE_QUEST_OFFERED,
        message,
        {
            "side_quest_id": side_quest.id,
            "offer_id": offer.id,
            **told,
            "announcement": side_quest.description,
            "difficulty": side_quest.difficulty.value,
            "exp_reward": side_quest.exp_reward,
            "penalty_exp": side_quest.penalty_exp,
            "expires_at": (
                side_quest.expires_at.isoformat() if side_quest.expires_at else None
            ),
            "auto_accepted": accepted,
        },
    )
    return offer


def _narrate(
    db: Session,
    player: Player,
    side_quest: SideQuest,
    kind: str,
    *,
    seed: int,
    standing: Standing | None = None,
) -> tuple[str, dict]:
    """The line to log, plus the story fields every side quest event carries.

    The message is what the constellation says; the title, the rank and the
    numbers ride on the payload. That split is deliberate — the feed reads as
    a voice rather than a receipt, and a client can still render a card from
    the structured half without parsing prose.
    """
    constellation = side_quest.constellation
    if standing is None:
        standing = constellations.standing_of(db, player, constellation)

    line = constellations.line_for(
        side_quest, constellation, kind, standing, seed=seed
    )
    name = constellation.name if constellation else None
    message = f"{name}: {line}" if name and line else (line or side_quest.title)

    return message, {
        "title": side_quest.title,
        "line": line,
        "constellation": constellation.code if constellation else None,
        "constellation_name": name,
        "standing": standing.value,
    }


def _favor_payload(change) -> dict:
    """How a constellation's regard moved, for the client to render."""
    if change is None:
        return {}
    return {
        "favor": change.after,
        "favor_delta": change.delta,
        "standing_changed": change.band_changed,
    }


def cancel_side_quest(
    db: Session,
    side_quest: SideQuest,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> int:
    """Call a broadcast off, voiding every offer still live.

    Withdrawn offers never penalize, whatever the broadcast's `penalty_exp`
    says — the quest was taken away, not failed. Returns how many were voided.
    """
    now = now or clock.utcnow()

    live = db.scalars(
        select(SideQuestOffer).where(
            SideQuestOffer.side_quest_id == side_quest.id,
            SideQuestOffer.status.in_(
                [SideQuestOfferStatus.OFFERED, SideQuestOfferStatus.ACCEPTED]
            ),
        )
    ).all()

    for offer in live:
        offer.status = SideQuestOfferStatus.WITHDRAWN
        player = db.get(Player, offer.player_id)
        if player is not None:
            friendship.settle_challenge(db, player, offer, settings, now=now)
            log_event(
                db,
                player,
                EventType.SIDE_QUEST_WITHDRAWN,
                f"Side quest withdrawn: {side_quest.title}",
                {"side_quest_id": side_quest.id, "offer_id": offer.id},
            )

    side_quest.status = SideQuestStatus.CANCELLED
    return len(live)


# --------------------------------------------------------------------------
# The player's side: answering, progressing, lapsing
# --------------------------------------------------------------------------


def get_offer(db: Session, player: Player, offer_id: int) -> SideQuestOffer:
    """Fetch one of the player's offers, or raise NotFoundError."""
    offer = db.scalar(
        select(SideQuestOffer).where(
            SideQuestOffer.id == offer_id, SideQuestOffer.player_id == player.id
        )
    )
    if offer is None:
        raise NotFoundError(f"No side quest offer with id {offer_id}.")
    return offer


def list_offers(
    db: Session,
    player: Player,
    *,
    status: SideQuestOfferStatus | None = None,
    live_only: bool = False,
) -> list[SideQuestOffer]:
    """The player's offers, newest first."""
    stmt = select(SideQuestOffer).where(SideQuestOffer.player_id == player.id)
    if status is not None:
        stmt = stmt.where(SideQuestOffer.status == status)
    if live_only:
        stmt = stmt.where(
            SideQuestOffer.status.in_(
                [SideQuestOfferStatus.OFFERED, SideQuestOfferStatus.ACCEPTED]
            )
        )
    return list(
        db.scalars(
            stmt.order_by(SideQuestOffer.offered_at.desc(), SideQuestOffer.id.desc())
        )
    )


def accept_offer(
    db: Session, player: Player, offer: SideQuestOffer, *, now: datetime | None = None
) -> SideQuestOffer:
    """Take a side quest up. From here it can be completed — or failed."""
    now = now or clock.utcnow()

    if offer.status is SideQuestOfferStatus.ACCEPTED:
        raise ValidationError("This side quest has already been accepted.")
    if offer.status is not SideQuestOfferStatus.OFFERED:
        raise ValidationError(
            f"This side quest is {offer.status.value}; it can no longer be accepted."
        )
    if offer.has_lapsed(now):
        raise ValidationError("This side quest's window has closed.")

    offer.status = SideQuestOfferStatus.ACCEPTED
    offer.responded_at = now

    side_quest = db.get(SideQuest, offer.side_quest_id)
    message, told = _narrate(db, player, side_quest, story.ACCEPT, seed=offer.id)

    log_event(
        db,
        player,
        EventType.SIDE_QUEST_ACCEPTED,
        message,
        {"side_quest_id": offer.side_quest_id, "offer_id": offer.id, **told},
    )
    return offer


def decline_offer(
    db: Session,
    player: Player,
    offer: SideQuestOffer,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> SideQuestOffer:
    """Pass on a side quest. Costs nothing, now or later.

    Declining a trial of admission is allowed too — it withdraws the request
    and starts the wait, the same as failing it. Changing your mind about
    asking is a thing people do.
    """
    now = now or clock.utcnow()

    if offer.status is not SideQuestOfferStatus.OFFERED:
        raise ValidationError(
            f"This side quest is {offer.status.value}; it can no longer be declined."
        )

    offer.status = SideQuestOfferStatus.DECLINED
    offer.responded_at = now

    side_quest = db.get(SideQuest, offer.side_quest_id)
    change = constellations.record_outcome(
        db,
        player,
        side_quest.constellation if side_quest else None,
        SideQuestOfferStatus.DECLINED,
        side_quest.difficulty if side_quest else QuestDifficulty.E,
        now=now,
    )
    message, told = _narrate(
        db,
        player,
        side_quest,
        story.DECLINE,
        seed=offer.id,
        standing=change.standing_after if change else None,
    )

    log_event(
        db,
        player,
        EventType.SIDE_QUEST_DECLINED,
        message,
        {
            "side_quest_id": offer.side_quest_id,
            "offer_id": offer.id,
            **told,
            **_favor_payload(change),
        },
    )

    friendship.settle_challenge(db, player, offer, settings, now=now)
    return offer


def add_progress(
    db: Session,
    player: Player,
    offer: SideQuestOffer,
    amount: int,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> tuple[SideQuestOffer, bool]:
    """Record progress on an accepted side quest, clearing it at its target.

    Returns the offer and whether this call completed it.
    """
    now = now or clock.utcnow()

    if amount == 0:
        raise ValidationError("Progress amount must not be zero.")
    if offer.status is SideQuestOfferStatus.OFFERED:
        raise ValidationError("Accept this side quest before logging progress.")
    if offer.status is not SideQuestOfferStatus.ACCEPTED:
        raise ValidationError(
            f"This side quest is {offer.status.value}; it cannot take progress."
        )
    if offer.has_lapsed(now):
        raise ValidationError("This side quest's window has closed.")

    offer.progress = max(0, offer.progress + amount)

    side_quest = db.get(SideQuest, offer.side_quest_id)
    # Progress is the one side quest event with no voice behind it: nobody
    # comments on your ninth rep, and a client renders this as a counter.
    log_event(
        db,
        player,
        EventType.SIDE_QUEST_PROGRESS,
        f"{side_quest.title if side_quest else 'Side quest'}: "
        f"{offer.progress}/{offer.target_count}",
        {
            "side_quest_id": offer.side_quest_id,
            "offer_id": offer.id,
            "progress": offer.progress,
            "target_count": offer.target_count,
        },
    )

    if offer.is_cleared:
        complete_offer(db, player, offer, settings, now=now)
        return offer, True

    return offer, False


def complete_offer(
    db: Session,
    player: Player,
    offer: SideQuestOffer,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> SideQuestOffer:
    """Clear a side quest and pay out what the broadcast promised."""
    now = now or clock.utcnow()

    if offer.status is SideQuestOfferStatus.COMPLETED:
        raise ValidationError("This side quest is already completed.")
    if offer.status is not SideQuestOfferStatus.ACCEPTED:
        raise ValidationError(
            f"This side quest is {offer.status.value}; it cannot be cleared."
        )

    side_quest = db.get(SideQuest, offer.side_quest_id)
    if side_quest is None:
        raise NotFoundError("The side quest behind this offer no longer exists.")

    offer.status = SideQuestOfferStatus.COMPLETED
    offer.progress = max(offer.progress, offer.target_count)
    offer.completed_at = now

    if side_quest.stat_reward is not None and side_quest.stat_reward_amount:
        player.add_stat(side_quest.stat_reward, side_quest.stat_reward_amount)

    result = award_exp(
        db,
        player,
        side_quest.exp_reward,
        settings,
        source=f"side_quest:{side_quest.id}",
    )

    change = constellations.record_outcome(
        db,
        player,
        side_quest.constellation,
        SideQuestOfferStatus.COMPLETED,
        side_quest.difficulty,
        now=now,
    )
    message, told = _narrate(
        db,
        player,
        side_quest,
        story.COMPLETE,
        seed=offer.id,
        standing=change.standing_after if change else None,
    )

    log_event(
        db,
        player,
        EventType.SIDE_QUEST_COMPLETED,
        f"{message} (+{side_quest.exp_reward} EXP)",
        {
            "side_quest_id": side_quest.id,
            "offer_id": offer.id,
            **told,
            **_favor_payload(change),
            "exp_gained": side_quest.exp_reward,
            "stat_reward": (
                side_quest.stat_reward.value if side_quest.stat_reward else None
            ),
            "stat_reward_amount": side_quest.stat_reward_amount,
            "leveled_up": result.leveled_up,
        },
    )

    friendship.settle_challenge(db, player, offer, settings, now=now)
    return offer


@dataclass
class SweepResult:
    """What one expiry sweep did to a player's offers."""

    expired_offer_ids: list[int] = field(default_factory=list)
    failed_offer_ids: list[int] = field(default_factory=list)
    total_exp_lost: int = 0

    @property
    def expired_count(self) -> int:
        return len(self.expired_offer_ids)

    @property
    def failed_count(self) -> int:
        return len(self.failed_offer_ids)

    @property
    def did_anything(self) -> bool:
        return bool(self.expired_offer_ids or self.failed_offer_ids)


def sweep_offers(
    db: Session,
    player: Player,
    settings: Settings,
    *,
    now: datetime | None = None,
) -> SweepResult:
    """Close out the player's offers whose windows have passed.

    The split that matters: an offer never answered simply EXPIRES and costs
    nothing, while one that was accepted and left unfinished FAILS and pays
    the broadcast's penalty. Ignoring the System is free; going back on a
    quest you took is not.

    Idempotent — a swept offer leaves the two live statuses behind, so running
    this twice cannot penalize twice.
    """
    now = now or clock.utcnow()
    result = SweepResult()

    # Sessions here do not autoflush, so an offer accepted or cleared earlier
    # in this same session would still read as live from the database. Flush
    # first, or the sweep settles something that has already been answered.
    db.flush()

    lapsed = db.scalars(
        select(SideQuestOffer)
        .where(
            SideQuestOffer.player_id == player.id,
            SideQuestOffer.status.in_(
                [SideQuestOfferStatus.OFFERED, SideQuestOfferStatus.ACCEPTED]
            ),
            SideQuestOffer.expires_at.is_not(None),
            SideQuestOffer.expires_at <= now,
        )
        .order_by(SideQuestOffer.id)
    ).all()

    for offer in lapsed:
        side_quest = db.get(SideQuest, offer.side_quest_id)
        title = side_quest.title if side_quest else "a side quest"
        constellation = side_quest.constellation if side_quest else None
        difficulty = side_quest.difficulty if side_quest else QuestDifficulty.E

        if offer.status is SideQuestOfferStatus.OFFERED:
            offer.status = SideQuestOfferStatus.EXPIRED
            result.expired_offer_ids.append(offer.id)

            change = constellations.record_outcome(
                db, player, constellation, SideQuestOfferStatus.EXPIRED, difficulty,
                now=now,
            )
            message, told = _narrate(
                db, player, side_quest, story.EXPIRE, seed=offer.id,
                standing=change.standing_after if change else None,
            ) if side_quest else (f"Side quest passed you by: {title}", {})

            log_event(
                db,
                player,
                EventType.SIDE_QUEST_EXPIRED,
                message,
                {
                    "side_quest_id": offer.side_quest_id,
                    "offer_id": offer.id,
                    **told,
                    **_favor_payload(change),
                },
            )
            friendship.settle_challenge(db, player, offer, settings, now=now)
            continue

        offer.status = SideQuestOfferStatus.FAILED
        result.failed_offer_ids.append(offer.id)

        change = constellations.record_outcome(
            db, player, constellation, SideQuestOfferStatus.FAILED, difficulty, now=now
        )
        message, told = _narrate(
            db, player, side_quest, story.FAIL, seed=offer.id,
            standing=change.standing_after if change else None,
        ) if side_quest else (f"Side quest failed: {title}", {})

        log_event(
            db,
            player,
            EventType.SIDE_QUEST_FAILED,
            message,
            {
                "side_quest_id": offer.side_quest_id,
                "offer_id": offer.id,
                **told,
                **_favor_payload(change),
                "progress": offer.progress,
                "target_count": offer.target_count,
            },
        )
        friendship.settle_challenge(db, player, offer, settings, now=now)

        penalty_exp = side_quest.penalty_exp if side_quest else 0
        amount = round(penalty_exp * settings.penalty_exp_multiplier)
        if amount > 0:
            penalty = apply_exp_penalty(
                db,
                player,
                amount,
                reason=f"Failed side quest: {title}",
                side_quest_offer=offer,
            )
            result.total_exp_lost += penalty.exp_lost

    return result


def close_finished_broadcasts(db: Session, *, now: datetime | None = None) -> int:
    """Mark broadcasts CLOSED once their window is behind us.

    Bookkeeping only — offers are settled per player by `sweep_offers`, which
    runs on the player's own schedule. Returns how many were closed.
    """
    now = now or clock.utcnow()

    finished = db.scalars(
        select(SideQuest).where(
            SideQuest.status == SideQuestStatus.BROADCAST,
            SideQuest.expires_at.is_not(None),
            SideQuest.expires_at <= now,
        )
    ).all()

    for side_quest in finished:
        side_quest.status = SideQuestStatus.CLOSED
    return len(finished)
