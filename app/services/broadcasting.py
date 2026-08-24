"""Putting written trials on the calendar.

The catalog in `content/broadcasts.py` says what the constellations have to
say; this decides which of it goes out and when. Kept apart from
`services/side_quests.py` on purpose: that module runs the machinery of an
already-scheduled broadcast, and knows nothing about where one came from.

The selection rule is "least recently sent, never the same trial twice in a
row", not a random draw. Two reasons: a rotation means every trial in the
catalog is seen before any of them repeats, and a deterministic pick is a
thing tests can pin down.
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
) -> BroadcastEntry | None:
    """Which trial to send next, or None if every one of them is resting.

    Never-sent entries come first, in catalog order; after that, the one that
    has been waiting longest. An entry inside its cooldown is skipped
    entirely, which is what stops a small catalog from repeating itself.
    """
    now = now or clock.utcnow()
    history = last_sent(db)
    cutoff = now - timedelta(days=COOLDOWN_DAYS)

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
    db: Session, *, at: datetime | None = None, now: datetime | None = None
) -> Scheduled | None:
    """Put the next trial in the rotation on the calendar, if one is ready."""
    now = now or clock.utcnow()
    entry = next_entry(db, now=now)
    if entry is None:
        return None
    return schedule(db, entry, at=at, now=now)


def has_open_broadcast(db: Session, *, now: datetime | None = None) -> bool:
    """Whether something is already out there.

    The cron entrypoint uses this to keep the sky quiet while a trial is still
    running: "from time to time" should not mean three at once.
    """
    now = now or clock.utcnow()
    found = db.scalar(
        select(SideQuest.id)
        .where(
            SideQuest.status.in_(
                [SideQuestStatus.SCHEDULED, SideQuestStatus.BROADCAST]
            ),
            (SideQuest.expires_at.is_(None)) | (SideQuest.expires_at > now),
        )
        .limit(1)
    )
    return found is not None


def ensure_pantheon(db: Session) -> None:
    """Seed the pantheon if it is not there yet, so scheduling never trips on it."""
    if not constellations.list_constellations(db, include_retired=True):
        constellations.seed_pantheon(db)
