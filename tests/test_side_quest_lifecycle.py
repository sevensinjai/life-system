"""Answering a side quest: accepting, clearing, and the two ways it can end."""

from datetime import UTC, datetime, timedelta

import pytest

from app.errors import ValidationError
from app.models import (
    EventType,
    Penalty,
    Player,
    SideQuestOfferStatus,
    StatName,
    SystemEvent,
    User,
)
from app.security import hash_password
from app.services import constellations, side_quests
from app.services.daily import run_daily_reset
from tests.conftest import befriend

NOW = datetime(2026, 8, 24, 12, tzinfo=UTC)
DEADLINE = NOW + timedelta(days=2)
AFTER = NOW + timedelta(days=3)


@pytest.fixture
def hunter(db) -> Player:
    user = User(email="hunter@example.com", hashed_password=hash_password("x" * 12))
    db.add(user)
    db.flush()
    player = Player(user_id=user.id, name="Sung Jinwoo", timezone="Asia/Seoul")
    db.add(player)
    db.flush()
    side_quests.set_preference(db, player, is_opted_in=True, now=NOW)
    return player


@pytest.fixture
def xingtian(db, hunter):
    """The pantheon, seeded, with the player already a friend of this one.

    A constellation issues to its friends and nobody else, so a test about
    what happens *after* a trial arrives has to start from friendship.
    """
    constellations.seed_pantheon(db)
    star = constellations.get_by_code(db, "xingtian")
    befriend(db, hunter, star, when=NOW)
    return star


@pytest.fixture
def offer(db, hunter, xingtian):
    """One open offer, worth 200 EXP with a 100 EXP penalty for dropping it."""
    side_quest = side_quests.create_side_quest(
        db,
        title="Slay ten shadows",
        constellation=xingtian,
        target_count=10,
        unit="shadows",
        exp_reward=200,
        stat_reward=StatName.STRENGTH,
        stat_reward_amount=2,
        penalty_exp=100,
        expires_at=DEADLINE,
        now=NOW,
    )
    side_quests.broadcast(db, side_quest, now=NOW)
    return side_quests.list_offers(db, hunter)[0]


def events_of(db, player, event_type) -> list[SystemEvent]:
    db.flush()
    return [
        event
        for event in db.query(SystemEvent).filter_by(player_id=player.id)
        if event.event_type is event_type
    ]


# --------------------------------------------------------------------------
# Answering
# --------------------------------------------------------------------------


def test_a_broadcast_lands_in_the_system_log(db, hunter, offer) -> None:
    """The feed carries the constellation's voice, with the facts alongside."""
    announcement = events_of(db, hunter, EventType.SIDE_QUEST_OFFERED)[0]

    assert announcement.message.startswith("The Will That Remains: ")
    assert announcement.payload["constellation"] == "xingtian"
    assert announcement.payload["title"] == "Slay ten shadows"
    assert announcement.payload["penalty_exp"] == 100


def test_accepting_then_clearing_pays_out(db, hunter, offer, settings) -> None:
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    _, completed = side_quests.add_progress(db, hunter, offer, 10, settings, now=NOW)

    assert completed is True
    assert offer.status is SideQuestOfferStatus.COMPLETED
    assert hunter.total_exp_earned == 200
    assert hunter.strength == 12


def test_progress_before_accepting_is_refused(db, hunter, offer, settings) -> None:
    """The accept step is the consent; progress cannot bypass it."""
    with pytest.raises(ValidationError, match="Accept this side quest"):
        side_quests.add_progress(db, hunter, offer, 1, settings, now=NOW)


def test_a_declined_side_quest_cannot_be_accepted_later(
    db, hunter, offer, settings
) -> None:
    side_quests.decline_offer(db, hunter, offer, settings, now=NOW)

    with pytest.raises(ValidationError, match="declined"):
        side_quests.accept_offer(db, hunter, offer, now=NOW)


def test_accepting_after_the_window_closed_is_refused(db, hunter, offer) -> None:
    with pytest.raises(ValidationError, match="window has closed"):
        side_quests.accept_offer(db, hunter, offer, now=AFTER)


def test_completing_outright_skips_the_counting(db, hunter, offer, settings) -> None:
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    side_quests.complete_offer(db, hunter, offer, settings, now=NOW)

    assert offer.progress == 10
    assert hunter.total_exp_earned == 200


# --------------------------------------------------------------------------
# The two ways a window closes
# --------------------------------------------------------------------------


def test_an_unanswered_side_quest_expires_for_free(db, hunter, offer, settings) -> None:
    """Ignoring the System costs nothing — that is what makes opting in safe."""
    result = side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    assert offer.status is SideQuestOfferStatus.EXPIRED
    assert result.total_exp_lost == 0
    db.flush()
    assert db.query(Penalty).count() == 0


def test_an_accepted_side_quest_left_unfinished_fails(db, hunter, offer, settings) -> None:
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    side_quests.add_progress(db, hunter, offer, 4, settings, now=NOW)
    hunter.exp = 500

    result = side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    assert offer.status is SideQuestOfferStatus.FAILED
    assert result.total_exp_lost == 100
    assert hunter.exp == 400


def test_a_failure_penalty_points_at_the_offer(db, hunter, offer, settings) -> None:
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    hunter.exp = 500
    side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    db.flush()
    penalty = db.query(Penalty).one()
    assert penalty.side_quest_offer_id == offer.id
    assert penalty.quest_instance_id is None


def test_a_broadcast_with_no_penalty_costs_nothing_to_drop(db, hunter, settings) -> None:
    side_quest = side_quests.create_side_quest(
        db, title="A gentle errand", expires_at=DEADLINE, now=NOW
    )
    side_quests.broadcast(db, side_quest, now=NOW)
    open_offer = side_quests.list_offers(db, hunter)[0]
    side_quests.accept_offer(db, hunter, open_offer, now=NOW)
    hunter.exp = 500

    result = side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    assert open_offer.status is SideQuestOfferStatus.FAILED
    assert result.total_exp_lost == 0
    assert hunter.exp == 500


def test_sweeping_twice_does_not_penalize_twice(db, hunter, offer, settings) -> None:
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    hunter.exp = 500
    side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    again = side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    assert again.did_anything is False
    assert hunter.exp == 400


def test_an_offer_with_no_deadline_never_lapses(db, hunter, settings) -> None:
    side_quest = side_quests.create_side_quest(
        db, title="An open invitation", expires_at=None, now=NOW
    )
    side_quests.broadcast(db, side_quest, now=NOW)
    waiting = side_quests.list_offers(db, hunter)[0]

    side_quests.sweep_offers(db, hunter, settings, now=NOW + timedelta(days=365))

    assert waiting.status is SideQuestOfferStatus.OFFERED


def test_a_completed_side_quest_is_left_alone_by_the_sweep(
    db, hunter, offer, settings
) -> None:
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    side_quests.complete_offer(db, hunter, offer, settings, now=NOW)

    side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    assert offer.status is SideQuestOfferStatus.COMPLETED


# --------------------------------------------------------------------------
# The daily reset settles side quests too
# --------------------------------------------------------------------------


def test_the_daily_reset_settles_lapsed_side_quests(db, hunter, offer, settings) -> None:
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    hunter.exp = 500

    result = run_daily_reset(db, hunter, settings, now=AFTER)

    assert result.side_quests_failed == 1
    assert result.total_exp_lost == 100
    assert offer.status is SideQuestOfferStatus.FAILED


def test_the_daily_reset_reports_expiries_separately(db, hunter, offer, settings) -> None:
    result = run_daily_reset(db, hunter, settings, now=AFTER)

    assert result.side_quests_expired == 1
    assert result.side_quests_failed == 0
    assert result.total_exp_lost == 0


def test_a_quiet_reset_still_logs_nothing(db, hunter, offer, settings) -> None:
    """An open side quest is not an event; only a settled one is."""
    result = run_daily_reset(db, hunter, settings, now=NOW)

    assert result.did_anything is False
