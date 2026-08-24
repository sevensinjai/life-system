"""Period math: when a quest is due, and how long you have to finish it."""

from datetime import date

import pytest

from app.models.enums import ScheduleKind as K
from app.services.scheduling import (
    MAX_INTERVAL_DAYS,
    Period,
    Schedule,
    ScheduleError,
    current_period,
    describe,
    is_recurring,
    next_occurrence,
    normalize_days,
)

MON = date(2026, 8, 24)
TUE = date(2026, 8, 25)
WED = date(2026, 8, 26)
THU = date(2026, 8, 27)
SUN = date(2026, 8, 30)


# --- validation -------------------------------------------------------------

def test_weekdays_requires_at_least_one_day() -> None:
    with pytest.raises(ScheduleError, match="at least one day"):
        Schedule(K.WEEKDAYS)


def test_weekdays_rejects_out_of_range_days() -> None:
    with pytest.raises(ScheduleError, match="between 0"):
        Schedule(K.WEEKDAYS, days=(0, 7))


def test_interval_requires_a_length() -> None:
    with pytest.raises(ScheduleError, match="interval_days"):
        Schedule(K.INTERVAL)


def test_interval_rejects_zero_and_absurd_lengths() -> None:
    with pytest.raises(ScheduleError):
        Schedule(K.INTERVAL, interval_days=0)
    with pytest.raises(ScheduleError):
        Schedule(K.INTERVAL, interval_days=MAX_INTERVAL_DAYS + 1)


def test_config_belonging_to_another_kind_is_rejected() -> None:
    """Catches an author sending weekdays with a daily schedule by mistake."""
    with pytest.raises(ScheduleError, match="does not take specific weekdays"):
        Schedule(K.DAILY, days=(0, 1))
    with pytest.raises(ScheduleError, match="does not take interval_days"):
        Schedule(K.DAILY, interval_days=3)


def test_week_start_must_be_a_weekday() -> None:
    with pytest.raises(ScheduleError, match="week_start"):
        Schedule(K.WEEKLY, week_start=9)


def test_days_are_sorted_and_deduplicated() -> None:
    assert normalize_days([4, 0, 4, 2]) == (0, 2, 4)


# --- daily ------------------------------------------------------------------

def test_daily_period_is_a_single_day() -> None:
    assert current_period(Schedule(K.DAILY), MON) == Period(MON, MON)


def test_daily_next_occurrence_is_tomorrow() -> None:
    assert next_occurrence(Schedule(K.DAILY), MON) == TUE


# --- weekdays ---------------------------------------------------------------

def test_weekdays_is_due_only_on_its_days() -> None:
    mwf = Schedule(K.WEEKDAYS, days=(0, 2, 4))

    assert current_period(mwf, MON) == Period(MON, MON)
    assert current_period(mwf, TUE) is None
    assert current_period(mwf, WED) == Period(WED, WED)


def test_weekdays_skips_to_the_next_matching_day() -> None:
    mwf = Schedule(K.WEEKDAYS, days=(0, 2, 4))

    assert next_occurrence(mwf, MON) == WED
    assert next_occurrence(mwf, TUE) == WED


def test_weekdays_wraps_around_the_week() -> None:
    mondays_only = Schedule(K.WEEKDAYS, days=(0,))

    assert next_occurrence(mondays_only, MON) == date(2026, 8, 31)


# --- interval ---------------------------------------------------------------

def test_interval_gives_the_whole_window_to_finish() -> None:
    """'Every 3 days' means a 3-day window, not a single day to hit."""
    every_three = Schedule(K.INTERVAL, interval_days=3, anchor=MON)

    assert current_period(every_three, MON) == Period(MON, WED)
    assert current_period(every_three, TUE) == Period(MON, WED)
    assert current_period(every_three, WED) == Period(MON, WED)
    assert current_period(every_three, THU) == Period(THU, date(2026, 8, 29))


def test_interval_of_one_behaves_like_daily() -> None:
    every_day = Schedule(K.INTERVAL, interval_days=1, anchor=MON)

    assert current_period(every_day, WED) == Period(WED, WED)


def test_interval_is_not_due_before_its_anchor() -> None:
    future = Schedule(K.INTERVAL, interval_days=3, anchor=THU)

    assert current_period(future, MON) is None
    assert next_occurrence(future, MON) == THU


def test_interval_next_occurrence_is_the_following_window() -> None:
    every_three = Schedule(K.INTERVAL, interval_days=3, anchor=MON)

    assert next_occurrence(every_three, MON) == THU
    assert next_occurrence(every_three, TUE) == THU
    assert next_occurrence(every_three, THU) == date(2026, 8, 30)


def test_interval_windows_tile_without_gaps_or_overlap() -> None:
    every_four = Schedule(K.INTERVAL, interval_days=4, anchor=MON)
    seen = set()

    for offset in range(40):
        day = date.fromordinal(MON.toordinal() + offset)
        period = current_period(every_four, day)
        assert period is not None and period.covers(day)
        seen.add(period.start)

    assert len(seen) == 10  # 40 days / 4-day windows


# --- weekly -----------------------------------------------------------------

def test_weekly_period_spans_seven_days() -> None:
    weekly = Schedule(K.WEEKLY)

    assert current_period(weekly, MON) == Period(MON, SUN)
    assert current_period(weekly, THU) == Period(MON, SUN)
    assert current_period(weekly, SUN) == Period(MON, SUN)


def test_weekly_respects_a_custom_week_start() -> None:
    """A week starting Sunday puts Monday in the period that began the day before."""
    sunday_start = Schedule(K.WEEKLY, week_start=6)

    period = current_period(sunday_start, MON)
    assert period == Period(date(2026, 8, 23), date(2026, 8, 29))


def test_weekly_next_occurrence_is_the_next_week() -> None:
    assert next_occurrence(Schedule(K.WEEKLY), THU) == date(2026, 8, 31)


# --- once -------------------------------------------------------------------

def test_once_has_an_open_ended_period() -> None:
    period = current_period(Schedule(K.ONCE, anchor=MON), THU)

    assert period == Period(MON, None)
    assert period.length_days is None


def test_an_open_period_never_lapses() -> None:
    period = Period(MON, None)

    assert not period.has_lapsed(date(2030, 1, 1))
    assert period.covers(date(2030, 1, 1))


def test_once_never_comes_around_again() -> None:
    assert next_occurrence(Schedule(K.ONCE), MON) is None
    assert not is_recurring(Schedule(K.ONCE))
    assert is_recurring(Schedule(K.DAILY))


# --- period helpers ---------------------------------------------------------

def test_period_covers_its_bounds_inclusively() -> None:
    period = Period(MON, WED)

    assert period.covers(MON) and period.covers(WED)
    assert not period.covers(date(2026, 8, 23))
    assert not period.covers(THU)


def test_period_lapses_only_after_its_end() -> None:
    period = Period(MON, WED)

    assert not period.has_lapsed(WED)
    assert period.has_lapsed(THU)


def test_period_length() -> None:
    assert Period(MON, MON).length_days == 1
    assert Period(MON, SUN).length_days == 7


# --- labels -----------------------------------------------------------------

@pytest.mark.parametrize(
    "schedule,expected",
    [
        (Schedule(K.ONCE), "One-time"),
        (Schedule(K.DAILY), "Every day"),
        (Schedule(K.WEEKDAYS, days=(0, 2, 4)), "Every Mon, Wed, Fri"),
        (Schedule(K.WEEKDAYS, days=tuple(range(7))), "Every day"),
        (Schedule(K.INTERVAL, interval_days=3), "Every 3 days"),
        (Schedule(K.INTERVAL, interval_days=1), "Every day"),
        (Schedule(K.WEEKLY), "Every week (from Mon)"),
        (Schedule(K.WEEKLY, week_start=6), "Every week (from Sun)"),
    ],
)
def test_describe(schedule: Schedule, expected: str) -> None:
    assert describe(schedule) == expected
