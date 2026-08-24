"""Timezone-aware date helpers.

A daily quest resets at the player's local midnight, not UTC midnight. Every
"what day is it for this player" question funnels through here.
"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def utcnow() -> datetime:
    """Current time, timezone-aware, in UTC."""
    return datetime.now(UTC)


def resolve_timezone(name: str) -> ZoneInfo:
    """Look up an IANA timezone, falling back to UTC if it is unknown.

    A stale or misspelled zone should not take the whole daily reset down, so
    this degrades instead of raising.
    """
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo("UTC")


def is_valid_timezone(name: str) -> bool:
    """Whether `name` is a known IANA timezone."""
    try:
        ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return False
    return True


def local_date(timezone_name: str, now: datetime | None = None) -> date:
    """The calendar date it currently is in the given timezone."""
    moment = now or utcnow()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(resolve_timezone(timezone_name)).date()


def next_local_midnight(timezone_name: str, now: datetime | None = None) -> datetime:
    """The next instant the player's local date turns over, as UTC.

    The lock-screen widget renders one quote per local day, so it needs to know
    when that day ends in order to schedule its own refresh. Returned in UTC
    because that is what a client timeline wants to compare against.
    """
    zone = resolve_timezone(timezone_name)
    moment = now or utcnow()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    tomorrow = moment.astimezone(zone).date() + timedelta(days=1)
    # A handful of zones skip midnight on a DST boundary; ZoneInfo resolves
    # those to the adjacent real instant rather than raising.
    return datetime.combine(tomorrow, time.min, tzinfo=zone).astimezone(UTC)
