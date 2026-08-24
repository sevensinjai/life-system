"""Authored schedules end to end: spawning, lapsing, and penalties.

The reset must treat every schedule kind the same way — a period that closes
unfinished lapses — so these exercise each kind through the real services.
"""

from datetime import date

import pytest

from app.models import Player, Quest, QuestInstance, QuestStatus, ScheduleKind as K
from app.services.daily import run_daily_reset
from app.services.quests import create_quest
from app.services.scheduling import Schedule
from tests.conftest import at

MON = date(2026, 8, 24)
TUE = date(2026, 8, 25)
WED = date(2026, 8, 26)


@pytest.fixture
def player(db) -> Player:
    """A UTC player, so test dates and local dates coincide."""
    from app.models import User
    from app.security import hash_password

    user = User(email="hunter@example.com", hashed_password=hash_password("x" * 12))
    db.add(user)
    db.flush()
    player = Player(user_id=user.id, name="Sung Jinwoo", timezone="UTC")
    db.add(player)
    db.commit()
    return player


def make(db, player, schedule: Schedule, *, today=MON, exp=100) -> Quest:
    quest = create_quest(
        db, player, title="Quest", schedule=schedule, exp_reward=exp, today=today
    )
    db.commit()
    return quest


def instances(db, quest) -> list[QuestInstance]:
    return (
        db.query(QuestInstance)
        .filter(QuestInstance.quest_id == quest.id)
        .order_by(QuestInstance.period_start)
        .all()
    )


# --- creation ---------------------------------------------------------------

def test_creating_on_a_due_day_opens_a_period(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.WEEKDAYS, days=(0,)), today=MON)

    assert len(instances(db, quest)) == 1


def test_creating_off_schedule_opens_nothing_yet(db, player, settings) -> None:
    """Authoring a Mon/Wed/Fri quest on a Tuesday should not open a period."""
    quest = make(db, player, Schedule(K.WEEKDAYS, days=(0, 2, 4)), today=TUE)

    assert instances(db, quest) == []


def test_interval_anchors_to_the_authoring_day(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.INTERVAL, interval_days=3), today=MON)

    assert quest.schedule_anchor == MON
    assert instances(db, quest)[0].period_end == WED


# --- spawning ---------------------------------------------------------------

def test_weekday_quest_spawns_only_on_its_days(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.WEEKDAYS, days=(0, 2)), today=MON)

    run_daily_reset(db, player, settings, now=at(2026, 8, 25))  # Tue
    db.commit()
    assert len(instances(db, quest)) == 1  # nothing new on Tuesday

    run_daily_reset(db, player, settings, now=at(2026, 8, 26))  # Wed
    db.commit()
    assert len(instances(db, quest)) == 2


def test_weekly_quest_spawns_once_per_week(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.WEEKLY), today=MON)

    for day in range(25, 31):  # Tue through Sun of the same week
        run_daily_reset(db, player, settings, now=at(2026, 8, day))
        db.commit()
    assert len(instances(db, quest)) == 1

    run_daily_reset(db, player, settings, now=at(2026, 8, 31))  # next Monday
    db.commit()
    assert len(instances(db, quest)) == 2


def test_interval_quest_spawns_once_per_window(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.INTERVAL, interval_days=3), today=MON)

    run_daily_reset(db, player, settings, now=at(2026, 8, 25))
    db.commit()
    assert len(instances(db, quest)) == 1  # still inside the first window

    run_daily_reset(db, player, settings, now=at(2026, 8, 27))
    db.commit()
    assert len(instances(db, quest)) == 2


# --- lapsing and penalties --------------------------------------------------

def test_a_weekly_period_survives_midweek(db, player, settings) -> None:
    """The whole point of a weekly quest: Tuesday must not fail it."""
    quest = make(db, player, Schedule(K.WEEKLY), today=MON)
    player.exp = 500
    db.commit()

    result = run_daily_reset(db, player, settings, now=at(2026, 8, 27))
    db.commit()

    assert result.failed_count == 0
    assert player.exp == 500
    assert instances(db, quest)[0].status is QuestStatus.ACTIVE


def test_a_weekly_period_lapses_once_the_week_ends(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.WEEKLY), today=MON)
    player.exp = 500
    db.commit()

    result = run_daily_reset(db, player, settings, now=at(2026, 8, 31))
    db.commit()

    assert result.failed_count == 1
    assert player.exp == 400
    assert instances(db, quest)[0].status is QuestStatus.FAILED


def test_an_interval_window_survives_until_the_next_one_opens(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.INTERVAL, interval_days=3), today=MON)
    player.exp = 500
    db.commit()

    # Day 2 of a 3-day window: still in hand.
    result = run_daily_reset(db, player, settings, now=at(2026, 8, 26))
    db.commit()
    assert result.failed_count == 0

    # Day 4: the window closed.
    result = run_daily_reset(db, player, settings, now=at(2026, 8, 27))
    db.commit()
    assert result.failed_count == 1
    assert player.exp == 400


def test_a_weekday_quest_lapses_the_next_day(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.WEEKDAYS, days=(0, 2)), today=MON)
    player.exp = 500
    db.commit()

    result = run_daily_reset(db, player, settings, now=at(2026, 8, 25))
    db.commit()

    assert result.failed_count == 1
    assert player.exp == 400


def test_completing_within_the_period_avoids_the_penalty(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.WEEKLY), today=MON)
    player.exp = 500
    instance = instances(db, quest)[0]
    instance.status = QuestStatus.COMPLETED
    db.commit()

    result = run_daily_reset(db, player, settings, now=at(2026, 8, 31))
    db.commit()

    assert result.failed_count == 0
    assert player.exp == 500


def test_a_one_time_quest_never_lapses(db, player, settings) -> None:
    quest = make(db, player, Schedule(K.ONCE), today=MON)
    player.exp = 500
    db.commit()

    result = run_daily_reset(db, player, settings, now=at(2027, 1, 1))
    db.commit()

    assert result.failed_count == 0
    assert player.exp == 500
    assert instances(db, quest)[0].status is QuestStatus.ACTIVE


def test_reset_is_idempotent_across_schedule_kinds(db, player, settings) -> None:
    for schedule in (
        Schedule(K.DAILY),
        Schedule(K.WEEKLY),
        Schedule(K.WEEKDAYS, days=(0, 2, 4)),
        Schedule(K.INTERVAL, interval_days=2),
    ):
        make(db, player, schedule, today=MON)

    first = run_daily_reset(db, player, settings, now=at(2026, 8, 27))
    db.commit()
    second = run_daily_reset(db, player, settings, now=at(2026, 8, 27, 20))
    db.commit()

    assert first.did_anything
    assert not second.did_anything
