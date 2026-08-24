"""When a quest comes around, and how long you have to finish it.

Pure by design — no ORM, no session, no ambient clock. Every function is a
function of its arguments, which is what makes the schedule rules cheap to
test exhaustively.

The central idea is the *period*: a window with a start and an optional end.
Progress accrues inside a period, and a period that ends unfinished lapses.
A daily quest's period is one day; a weekly quest's is seven. A one-time
quest's period never ends, so it can never lapse.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from app.models.enums import ScheduleKind

MAX_INTERVAL_DAYS = 365
DAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


class ScheduleError(ValueError):
    """A schedule whose configuration does not describe a real recurrence."""


@dataclass(frozen=True)
class Period:
    """A window a quest instance lives in. An open end never lapses."""

    start: date
    end: date | None

    def covers(self, day: date) -> bool:
        if day < self.start:
            return False
        return self.end is None or day <= self.end

    def has_lapsed(self, today: date) -> bool:
        return self.end is not None and self.end < today

    @property
    def length_days(self) -> int | None:
        return None if self.end is None else (self.end - self.start).days + 1


@dataclass(frozen=True)
class Schedule:
    """A quest's recurrence rule."""

    kind: ScheduleKind
    days: tuple[int, ...] = ()  # 0 = Monday .. 6 = Sunday, for WEEKDAYS
    interval_days: int | None = None  # for INTERVAL
    anchor: date | None = None  # the day the recurrence counts from
    week_start: int = 0  # 0 = Monday, for WEEKLY

    def __post_init__(self) -> None:
        validate(self)


def validate(schedule: Schedule) -> None:
    """Reject configurations that do not describe a real recurrence."""
    if not 0 <= schedule.week_start <= 6:
        raise ScheduleError("week_start must be between 0 (Monday) and 6 (Sunday).")

    if schedule.kind is ScheduleKind.WEEKDAYS:
        if not schedule.days:
            raise ScheduleError(
                "A weekdays schedule needs at least one day, "
                "where 0 is Monday and 6 is Sunday."
            )
        if any(not 0 <= day <= 6 for day in schedule.days):
            raise ScheduleError("Weekdays must be between 0 (Monday) and 6 (Sunday).")
    elif schedule.days:
        raise ScheduleError(
            f"A {schedule.kind.value} schedule does not take specific weekdays."
        )

    if schedule.kind is ScheduleKind.INTERVAL:
        if schedule.interval_days is None:
            raise ScheduleError("An interval schedule needs interval_days.")
        if schedule.interval_days < 1:
            raise ScheduleError("interval_days must be at least 1.")
        if schedule.interval_days > MAX_INTERVAL_DAYS:
            raise ScheduleError(
                f"interval_days must not exceed {MAX_INTERVAL_DAYS}."
            )
    elif schedule.interval_days is not None:
        raise ScheduleError(
            f"A {schedule.kind.value} schedule does not take interval_days."
        )


def normalize_days(days) -> tuple[int, ...]:
    """Sort and de-duplicate a set of weekdays."""
    return tuple(sorted(set(days)))


def is_recurring(schedule: Schedule) -> bool:
    return schedule.kind is not ScheduleKind.ONCE


def current_period(schedule: Schedule, today: date) -> Period | None:
    """The period covering `today`, or None if the quest is not due then.

    Only a WEEKDAYS schedule can return None for a date on or after its anchor:
    the other kinds tile the calendar without gaps.
    """
    match schedule.kind:
        case ScheduleKind.ONCE:
            # Open-ended: a one-time quest waits indefinitely.
            return Period(start=schedule.anchor or today, end=None)

        case ScheduleKind.DAILY:
            return Period(start=today, end=today)

        case ScheduleKind.WEEKDAYS:
            if today.weekday() not in schedule.days:
                return None
            return Period(start=today, end=today)

        case ScheduleKind.INTERVAL:
            anchor = schedule.anchor or today
            if today < anchor:
                return None
            span = schedule.interval_days or 1
            # An "every N days" quest gives you the whole N-day window to finish,
            # so it only lapses when the next occurrence opens.
            elapsed = (today - anchor).days
            start = anchor + timedelta(days=(elapsed // span) * span)
            return Period(start=start, end=start + timedelta(days=span - 1))

        case ScheduleKind.WEEKLY:
            offset = (today.weekday() - schedule.week_start) % 7
            start = today - timedelta(days=offset)
            return Period(start=start, end=start + timedelta(days=6))

    raise ScheduleError(f"Unhandled schedule kind: {schedule.kind}")


def next_occurrence(schedule: Schedule, after: date) -> date | None:
    """The start of the first period beginning strictly after `after`.

    None for a one-time quest, which never comes around again.
    """
    match schedule.kind:
        case ScheduleKind.ONCE:
            return None

        case ScheduleKind.DAILY:
            return after + timedelta(days=1)

        case ScheduleKind.WEEKDAYS:
            for step in range(1, 8):
                candidate = after + timedelta(days=step)
                if candidate.weekday() in schedule.days:
                    return candidate
            return None  # unreachable: validation guarantees a non-empty day set

        case ScheduleKind.INTERVAL:
            anchor = schedule.anchor or after
            if after < anchor:
                return anchor
            span = schedule.interval_days or 1
            elapsed = (after - anchor).days
            return anchor + timedelta(days=((elapsed // span) + 1) * span)

        case ScheduleKind.WEEKLY:
            offset = (after.weekday() - schedule.week_start) % 7
            return after - timedelta(days=offset) + timedelta(days=7)

    raise ScheduleError(f"Unhandled schedule kind: {schedule.kind}")


def describe(schedule: Schedule) -> str:
    """A human-readable summary, for the client to render under the title."""
    match schedule.kind:
        case ScheduleKind.ONCE:
            return "One-time"
        case ScheduleKind.DAILY:
            return "Every day"
        case ScheduleKind.WEEKDAYS:
            if len(schedule.days) == 7:
                return "Every day"
            return "Every " + ", ".join(DAY_NAMES[day] for day in schedule.days)
        case ScheduleKind.INTERVAL:
            span = schedule.interval_days or 1
            return "Every day" if span == 1 else f"Every {span} days"
        case ScheduleKind.WEEKLY:
            return f"Every week (from {DAY_NAMES[schedule.week_start]})"
    return schedule.kind.value
