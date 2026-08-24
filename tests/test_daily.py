"""The daily reset: expiry, penalties, respawn, and idempotency."""

from datetime import date, timedelta

import pytest

from app.models import Player, Quest, QuestInstance, QuestStatus, QuestType, StatName
from app.services.daily import run_daily_reset
from app.services.quests import create_quest, get_or_create_instance
from tests.conftest import at

DAY_ONE = date(2026, 8, 24)
DAY_TWO = date(2026, 8, 25)


@pytest.fixture
def seoul_player(db) -> Player:
    """A player in Asia/Seoul, so local midnight is clearly not UTC midnight."""
    from app.models import User
    from app.security import hash_password

    user = User(email="hunter@example.com", hashed_password=hash_password("x" * 12))
    db.add(user)
    db.flush()
    player = Player(user_id=user.id, name="Sung Jinwoo", timezone="Asia/Seoul")
    db.add(player)
    db.commit()
    return player


@pytest.fixture
def daily_quest(db, seoul_player, settings) -> Quest:
    quest = create_quest(
        db,
        seoul_player,
        title="100 push-ups",
        quest_type=QuestType.DAILY,
        target_count=100,
        exp_reward=100,
        today=DAY_ONE,
    )
    db.commit()
    return quest


def instance_for(db, quest: Quest, day: date) -> QuestInstance | None:
    return (
        db.query(QuestInstance)
        .filter(QuestInstance.quest_id == quest.id, QuestInstance.quest_date == day)
        .one_or_none()
    )


def test_reset_fails_yesterdays_untouched_daily(db, seoul_player, daily_quest, settings):
    # 03:00 UTC on day two is noon in Seoul — safely into the next local day.
    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()

    assert result.failed_count == 1
    assert instance_for(db, daily_quest, DAY_ONE).status is QuestStatus.FAILED


def test_reset_spawns_todays_instance(db, seoul_player, daily_quest, settings):
    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()

    assert result.spawned_count == 1
    fresh = instance_for(db, daily_quest, DAY_TWO)
    assert fresh is not None
    assert fresh.status is QuestStatus.ACTIVE
    assert fresh.progress == 0


def test_failing_a_daily_costs_exp(db, seoul_player, daily_quest, settings):
    seoul_player.exp = 250
    db.commit()

    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()

    assert result.total_exp_lost == 100  # the quest's reward, at multiplier 1.0
    assert seoul_player.exp == 150


def test_penalty_never_delevels_the_player(db, seoul_player, daily_quest, settings):
    seoul_player.level = 5
    seoul_player.exp = 30
    db.commit()

    run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()

    assert seoul_player.level == 5
    assert seoul_player.exp == 0


def test_penalty_records_only_what_was_actually_lost(db, seoul_player, daily_quest, settings):
    from app.models import Penalty

    seoul_player.exp = 30
    db.commit()

    run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()

    penalty = db.query(Penalty).one()
    assert penalty.exp_lost == 30  # not the full 100
    assert "100 push-ups" in penalty.reason


def test_completed_daily_is_not_penalized(db, seoul_player, daily_quest, settings):
    instance = instance_for(db, daily_quest, DAY_ONE)
    instance.status = QuestStatus.COMPLETED
    db.commit()

    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()

    assert result.failed_count == 0
    assert result.total_exp_lost == 0


def test_reset_is_idempotent_within_a_day(db, seoul_player, daily_quest, settings):
    first = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()
    second = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 9))
    db.commit()

    assert (first.failed_count, first.spawned_count) == (1, 1)
    assert (second.failed_count, second.spawned_count) == (0, 0)
    assert db.query(QuestInstance).count() == 2  # one per day, not three


def test_reset_within_the_same_local_day_does_nothing(db, seoul_player, daily_quest, settings):
    # 03:00 UTC on day one is noon in Seoul: still DAY_ONE locally.
    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 24, 3))
    db.commit()

    assert result.failed_count == 0
    assert result.spawned_count == 0


def test_timezone_decides_when_the_day_turns(db, seoul_player, daily_quest, settings):
    """20:00 UTC on day one is already 05:00 on day two in Seoul (UTC+9)."""
    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 24, 20))
    db.commit()

    assert result.failed_count == 1
    assert result.reset_date == DAY_TWO


def test_multiple_missed_days_each_fail_once(db, seoul_player, daily_quest, settings):
    """Three lapsed days cost three penalties, but only down to zero EXP."""
    for offset in (1, 2):
        get_or_create_instance(db, daily_quest, DAY_ONE + timedelta(days=offset))
    seoul_player.exp = 150
    db.commit()

    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 28, 3))
    db.commit()

    assert result.failed_count == 3  # day one, two, and three all lapsed
    # 100 taken, then only the remaining 50; the third finds nothing left.
    assert result.total_exp_lost == 150
    assert seoul_player.exp == 0
    statuses = {i.status for i in db.query(QuestInstance).filter(
        QuestInstance.quest_date < date(2026, 8, 28)
    )}
    assert statuses == {QuestStatus.FAILED}


def test_archived_daily_stops_spawning(db, seoul_player, daily_quest, settings):
    daily_quest.is_active = False
    db.commit()

    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 25, 3))
    db.commit()

    assert result.spawned_count == 0
    assert result.failed_count == 1  # the already-open instance still lapses


def test_normal_quests_are_never_penalized(db, seoul_player, settings):
    create_quest(
        db,
        seoul_player,
        title="Read a book",
        quest_type=QuestType.NORMAL,
        exp_reward=100,
        today=DAY_ONE,
    )
    db.commit()

    result = run_daily_reset(db, seoul_player, settings, now=at(2026, 8, 28, 3))
    db.commit()

    assert result.failed_count == 0
    assert result.total_exp_lost == 0


def test_penalty_multiplier_scales_the_loss(db, seoul_player, daily_quest, settings):
    seoul_player.exp = 500
    harsh = settings.model_copy(update={"penalty_exp_multiplier": 2.0})
    db.commit()

    result = run_daily_reset(db, seoul_player, harsh, now=at(2026, 8, 25, 3))
    db.commit()

    assert result.total_exp_lost == 200
    assert seoul_player.exp == 300


def test_reset_endpoint_is_safe_to_call_repeatedly(auth_client):
    auth_client.post("/quests", json={"title": "Run 10km", "quest_type": "daily"})

    first = auth_client.post("/system/daily-reset").json()
    second = auth_client.post("/system/daily-reset").json()

    assert first["failed_count"] == 0
    assert second == first
    assert len(auth_client.get("/quests/today").json()) == 1
