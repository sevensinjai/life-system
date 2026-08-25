"""Putting written trials on the calendar.

The catalog in `content/broadcasts.py` says what the constellations have to
say; this decides which of it goes out and when. Kept apart from
`services/side_quests.py` on purpose: that module runs the machinery of an
already-scheduled broadcast, and knows nothing about where one came from.

The selection rule is "least recently sent, never the same trial twice in a
row", not a random draw. Two reasons: a rotation means every trial in the
catalog is seen before any of them repeats, and a deterministic pick is a
thing tests can pin down.

Rotation is **per constellation**, not global. Each one works down its own
ladder independently, and each is allowed one open broadcast at a time. With
twenty-eight of them a single global slot would mean a player who befriended
three constellations heard from one of them a month; what rations the noise is
the player's own weekly cap, not a bottleneck in the sky.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.broadcasts import BROADCASTS, BroadcastEntry, as_lines_payload
from app.errors import NotFoundError, ValidationError
from app.models import Constellation, SideQuest, SideQuestStatus
from app.services import clock, constellations

# How long a trial rests after being sent before it may be sent again.
COOLDOWN_DAYS = 30


@dataclass
class Scheduled:
    """One catalog entry placed on the calendar."""

    entry: BroadcastEntry
    side_quest: SideQuest


def entry_by_code(code: str) -> BroadcastEntry:
    """One written trial, or raise NotFoundError."""
    for entry in BROADCASTS:
        if entry.code == code:
            return entry
    raise NotFoundError(f"No broadcast in the catalog with code {code!r}.")


def last_sent(db: Session) -> dict[str, datetime]:
    """When each catalog entry last went out, for entries that ever have."""
    rows = db.execute(
        select(SideQuest.catalog_code, SideQuest.broadcast_at)
        .where(SideQuest.catalog_code.is_not(None))
        .order_by(SideQuest.broadcast_at)
    ).all()
    return {code: broadcast_at for code, broadcast_at in rows}


def next_entry(
    db: Session,
    *,
    now: datetime | None = None,
    catalog: tuple[BroadcastEntry, ...] = BROADCASTS,
    constellation: str | None = None,
) -> BroadcastEntry | None:
    """Which trial to send next, or None if every candidate is resting.

    Never-sent entries come first, in catalog order — which is the ladder
    order, so a constellation works up from its easiest rungs — and after that
    the one that has been waiting longest. An entry inside its cooldown is
    skipped entirely, which is what stops a constellation from repeating
    itself while it still has unsent trials.

    Pass `constellation` to draw from one figure's ladder alone.
    """
    now = now or clock.utcnow()
    history = last_sent(db)
    cutoff = now - timedelta(days=COOLDOWN_DAYS)

    if constellation is not None:
        catalog = tuple(e for e in catalog if e.constellation == constellation)

    unsent = [entry for entry in catalog if entry.code not in history]
    if unsent:
        return unsent[0]

    rested = [
        entry
        for entry in catalog
        if clock.as_utc(history[entry.code]) <= clock.as_utc(cutoff)
    ]
    if not rested:
        return None
    return min(rested, key=lambda entry: clock.as_utc(history[entry.code]))


def schedule(
    db: Session,
    entry: BroadcastEntry,
    *,
    at: datetime | None = None,
    now: datetime | None = None,
) -> Scheduled:
    """Place one written trial on the calendar.

    Scheduled, not sent: `side_quests.dispatch_due` picks it up when its
    moment arrives, which keeps "what goes out" and "when it goes out" as
    separate decisions.
    """
    from app.services.side_quests import create_side_quest

    now = now or clock.utcnow()
    at = at or now

    constellation: Constellation | None = None
    if entry.constellation:
        constellation = db.scalar(
            select(Constellation).where(Constellation.code == entry.constellation)
        )
        if constellation is None:
            raise ValidationError(
                f"The pantheon has no constellation {entry.constellation!r}; "
                "seed it before scheduling its trials."
            )

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
        broadcast_at=at,
        expires_at=at + timedelta(hours=entry.window_hours),
        min_level=entry.min_level,
        max_level=entry.max_level,
        min_standing=entry.min_standing,
        now=now,
    )
    return Scheduled(entry=entry, side_quest=side_quest)


def schedule_next(
    db: Session,
    *,
    at: datetime | None = None,
    now: datetime | None = None,
    constellation: str | None = None,
) -> Scheduled | None:
    """Put the next trial in the rotation on the calendar, if one is ready."""
    now = now or clock.utcnow()
    entry = next_entry(db, now=now, constellation=constellation)
    if entry is None:
        return None
    return schedule(db, entry, at=at, now=now)


def schedule_due_constellations(
    db: Session, *, now: datetime | None = None
) -> list[Scheduled]:
    """Give every constellation with nothing open its next trial.

    Each figure keeps its own rotation and its own single open slot, so the
    sky as a whole is busy while any one voice stays occasional. What a
    player actually receives is decided further down, by their friendships
    and their weekly cap.
    """
    now = now or clock.utcnow()

    scheduled = []
    for constellation in constellations.list_constellations(db):
        if has_open_broadcast(db, now=now, constellation_id=constellation.id):
            continue
        placed = schedule_next(db, now=now, constellation=constellation.code)
        if placed is not None:
            scheduled.append(placed)
    return scheduled


def has_open_broadcast(
    db: Session,
    *,
    now: datetime | None = None,
    constellation_id: int | None = None,
) -> bool:
    """Whether something is already out there, from anyone or from one figure.

    Used to keep a constellation quiet while its own trial is still running:
    "from time to time" should not mean three at once from the same voice.
    """
    now = now or clock.utcnow()
    stmt = select(SideQuest.id).where(
        SideQuest.status.in_([SideQuestStatus.SCHEDULED, SideQuestStatus.BROADCAST]),
        (SideQuest.expires_at.is_(None)) | (SideQuest.expires_at > now),
        # One player's trial of admission is not the sky being busy.
        SideQuest.is_challenge.is_(False),
    )
    if constellation_id is not None:
        stmt = stmt.where(SideQuest.constellation_id == constellation_id)
    return db.scalar(stmt.limit(1)) is not None


def ensure_pantheon(db: Session) -> None:
    """Seed the pantheon if it is not there yet, so scheduling never trips on it."""
    if not constellations.list_constellations(db, include_retired=True):
        constellations.seed_pantheon(db)
