"""The pure rotation: which quote a given day lands on."""

from datetime import date, timedelta

import pytest

from app.services.clock import next_local_midnight
from app.services.quotes import normalize_text, pick_for_day
from tests.conftest import at


def test_an_empty_collection_has_no_quote_for_today() -> None:
    assert pick_for_day([], date(2026, 8, 24)) is None


def test_the_same_day_always_resolves_to_the_same_quote() -> None:
    """A widget may ask many times a day; it must not get a different answer."""
    ids = [4, 8, 15, 16, 23, 42]
    day = date(2026, 8, 24)

    assert len({pick_for_day(ids, day) for _ in range(50)}) == 1


def test_consecutive_days_step_through_the_pool() -> None:
    """Each day advances one place and wraps.

    Which entry a given date starts on falls out of its ordinal, so the test
    asserts the stepping itself rather than a fixed starting point.
    """
    ids = [3, 7, 9]
    start = date(2026, 8, 24)

    picks = [pick_for_day(ids, start + timedelta(days=n)) for n in range(6)]

    first = ids.index(picks[0])
    assert picks == [ids[(first + n) % len(ids)] for n in range(6)]
    assert picks[3:] == picks[:3]  # and the cycle repeats


def test_every_quote_is_seen_before_any_repeats() -> None:
    """The point of a rotation over a random draw: no early repeats."""
    ids = list(range(1, 13))
    start = date(2026, 1, 1)

    first_pass = [pick_for_day(ids, start + timedelta(days=n)) for n in range(len(ids))]

    assert sorted(first_pass) == ids


def test_a_single_quote_is_shown_every_day() -> None:
    start = date(2026, 8, 24)

    picks = [pick_for_day([5], start + timedelta(days=n)) for n in range(4)]

    assert picks == [5, 5, 5, 5]


@pytest.mark.parametrize("size", range(1, 32))
def test_the_pick_is_always_in_the_pool(size: int) -> None:
    ids = list(range(100, 100 + size))
    start = date(2026, 3, 1)

    for offset in range(70):
        assert pick_for_day(ids, start + timedelta(days=offset)) in ids


def test_normalize_collapses_pasted_whitespace() -> None:
    assert normalize_text("  Arise,\n  and  keep going. ") == "Arise, and keep going."


def test_refresh_lands_on_the_players_next_local_midnight() -> None:
    """20:00 UTC is already tomorrow morning in Seoul, so its midnight is nearer."""
    now = at(2026, 8, 24, hour=20)

    seoul = next_local_midnight("Asia/Seoul", now)
    utc = next_local_midnight("UTC", now)

    assert seoul.isoformat() == "2026-08-25T15:00:00+00:00"
    assert utc.isoformat() == "2026-08-25T00:00:00+00:00"
    assert seoul > now and utc > now


def test_refresh_survives_a_zone_that_skips_midnight() -> None:
    """Santiago jumps 24:00 to 01:00 on a DST boundary; it must still resolve."""
    moment = next_local_midnight("America/Santiago", at(2026, 9, 5, hour=20))

    assert moment.isoformat() == "2026-09-06T04:00:00+00:00"
