"""The opt-in: who hears the System's broadcasts, and how often."""

from datetime import UTC, datetime, timedelta

import pytest

from app.models import (
    Player,
    QuestDifficulty,
    SideQuestFrequency,
    SideQuestOfferStatus,
    SideQuestStatus,
    User,
)
from app.security import hash_password
from app.services import side_quests
from app.services.clock import as_utc

NOW = datetime(2026, 8, 24, 12, tzinfo=UTC)


def make_player(db, email: str, name: str, level: int = 1) -> Player:
    user = User(email=email, hashed_password=hash_password("x" * 12))
    db.add(user)
    db.flush()
    player = Player(user_id=user.id, name=name, level=level, timezone="Asia/Seoul")
    db.add(player)
    db.flush()
    return player


@pytest.fixture
def hunter(db) -> Player:
    return make_player(db, "hunter@example.com", "Sung Jinwoo")


def broadcast_now(db, *, now=NOW, **kwargs):
    """Author a side quest and put it out immediately."""
    kwargs.setdefault("title", "Slay ten shadows")
    kwargs.setdefault("expires_at", now + timedelta(days=2))
    side_quest = side_quests.create_side_quest(db, now=now, **kwargs)
    result = side_quests.broadcast(db, side_quest, now=now)
    return side_quest, result


# --------------------------------------------------------------------------
# The default answer
# --------------------------------------------------------------------------


def test_a_player_who_never_answered_is_opted_out(db, hunter) -> None:
    """Nobody is enrolled quietly — the default has to be no."""
    preference = side_quests.get_preference(db, hunter)

    assert preference.is_opted_in is False
    assert preference.opted_in_at is None


def test_the_default_preference_is_not_persisted(db, hunter) -> None:
    """Reading the setting must not create a row, or "never asked" is lost."""
    side_quests.get_preference(db, hunter)

    from app.models import SideQuestPreference

    assert db.query(SideQuestPreference).count() == 0


def test_an_opted_out_player_receives_nothing(db, hunter) -> None:
    _, result = broadcast_now(db)

    assert result.offered_count == 0
    assert side_quests.list_offers(db, hunter) == []


def test_opting_in_records_when(db, hunter) -> None:
    preference = side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)

    assert preference.is_opted_in is True
    assert as_utc(preference.opted_in_at) == NOW
    assert preference.opted_out_at is None


def test_opting_out_again_keeps_both_dates(db, hunter) -> None:
    """The System can tell someone who stopped listening from someone who never did."""
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    later = NOW + timedelta(days=3)
    preference = side_quests.set_preference(db, hunter, is_opted_in=False, now=later)

    assert as_utc(preference.opted_in_at) == NOW
    assert as_utc(preference.opted_out_at) == later


def test_re_stating_the_same_answer_does_not_move_the_date(db, hunter) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quests.set_preference(
        db, hunter, is_opted_in=True, frequency=SideQuestFrequency.RARE,
        now=NOW + timedelta(days=1),
    )

    assert as_utc(side_quests.get_preference(db, hunter).opted_in_at) == NOW


# --------------------------------------------------------------------------
# Reaching the people who said yes
# --------------------------------------------------------------------------


def test_a_broadcast_reaches_everyone_listening(db) -> None:
    listeners = [
        make_player(db, f"hunter{i}@example.com", f"Hunter {i}") for i in range(3)
    ]
    for player in listeners[:2]:
        side_quests.set_preference(db, player, is_opted_in=True, now=NOW)

    _, result = broadcast_now(db)

    assert result.offered_count == 2
    assert result.offered_player_ids == [listeners[0].id, listeners[1].id]


def test_an_offer_snapshots_the_target_and_the_deadline(db, hunter) -> None:
    """Retuning a broadcast mid-flight must not move anyone's goalposts."""
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quest, _ = broadcast_now(db, target_count=10, unit="shadows")

    offer = side_quests.list_offers(db, hunter)[0]
    assert offer.target_count == 10
    assert as_utc(offer.expires_at) == as_utc(side_quest.expires_at)
    assert offer.status is SideQuestOfferStatus.OFFERED


def test_broadcasting_twice_does_not_offer_twice(db, hunter) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quest, _ = broadcast_now(db)

    again = side_quests.broadcast(db, side_quest, now=NOW + timedelta(hours=1))

    assert again.offered_count == 0
    assert again.skipped == {"already_offered": 1}
    assert len(side_quests.list_offers(db, hunter)) == 1


def test_a_rank_cap_filters_a_broadcast_out(db, hunter) -> None:
    side_quests.set_preference(
        db, hunter, is_opted_in=True, max_difficulty=QuestDifficulty.B, now=NOW
    )

    _, result = broadcast_now(db, difficulty=QuestDifficulty.S)

    assert result.offered_count == 0
    assert result.skipped == {"above_rank_cap": 1}


def test_a_rank_at_the_cap_still_gets_through(db, hunter) -> None:
    side_quests.set_preference(
        db, hunter, is_opted_in=True, max_difficulty=QuestDifficulty.B, now=NOW
    )

    _, result = broadcast_now(db, difficulty=QuestDifficulty.B)

    assert result.offered_count == 1


def test_lifting_the_rank_cap_takes_anything(db, hunter) -> None:
    side_quests.set_preference(
        db, hunter, is_opted_in=True, max_difficulty=QuestDifficulty.E, now=NOW
    )
    side_quests.set_preference(db, hunter, max_difficulty=None, now=NOW)

    _, result = broadcast_now(db, difficulty=QuestDifficulty.S)

    assert result.offered_count == 1


def test_a_level_range_filters_a_broadcast_out(db) -> None:
    rookie = make_player(db, "rookie@example.com", "Rookie", level=2)
    veteran = make_player(db, "veteran@example.com", "Veteran", level=40)
    for player in (rookie, veteran):
        side_quests.set_preference(db, player, is_opted_in=True, now=NOW)

    _, result = broadcast_now(db, min_level=30)

    assert result.offered_player_ids == [veteran.id]
    assert result.skipped == {"outside_level_range": 1}


# --------------------------------------------------------------------------
# "Occasionally": the frequency cap
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("frequency", "allowed"),
    [
        (SideQuestFrequency.RARE, 1),
        (SideQuestFrequency.OCCASIONAL, 3),
        (SideQuestFrequency.FREQUENT, 7),
    ],
)
def test_frequency_caps_offers_per_week(db, hunter, frequency, allowed) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, frequency=frequency, now=NOW)

    for i in range(10):
        broadcast_now(db, title=f"Trial {i}", now=NOW + timedelta(hours=i))

    assert len(side_quests.list_offers(db, hunter)) == allowed


def test_the_cap_is_a_rolling_week_not_a_calendar_one(db, hunter) -> None:
    side_quests.set_preference(
        db, hunter, is_opted_in=True, frequency=SideQuestFrequency.RARE, now=NOW
    )
    broadcast_now(db, title="First", now=NOW)

    # Six days on, the first offer still occupies the only slot.
    broadcast_now(db, title="Too soon", now=NOW + timedelta(days=6))
    assert len(side_quests.list_offers(db, hunter)) == 1

    # Eight days on, it has rolled out of the window.
    broadcast_now(db, title="Room again", now=NOW + timedelta(days=8))
    assert len(side_quests.list_offers(db, hunter)) == 2


def test_declining_still_uses_a_slot(db, hunter, settings) -> None:
    """The interruption is what the player rationed, not the acceptance."""
    side_quests.set_preference(
        db, hunter, is_opted_in=True, frequency=SideQuestFrequency.RARE, now=NOW
    )
    broadcast_now(db, title="First", now=NOW)
    offer = side_quests.list_offers(db, hunter)[0]
    side_quests.decline_offer(db, hunter, offer, settings, now=NOW)

    broadcast_now(db, title="Second", now=NOW + timedelta(hours=2))

    assert len(side_quests.list_offers(db, hunter)) == 1


# --------------------------------------------------------------------------
# Opting in late
# --------------------------------------------------------------------------


def test_opting_in_catches_up_on_open_broadcasts(db, hunter) -> None:
    """Saying yes should mean something now, not at the next broadcast."""
    broadcast_now(db, title="Still open", now=NOW)
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW + timedelta(hours=1))

    offers = side_quests.catch_up(db, hunter, now=NOW + timedelta(hours=1))

    assert len(offers) == 1


def test_catching_up_skips_broadcasts_that_already_closed(db, hunter) -> None:
    side_quest, _ = broadcast_now(db, now=NOW, expires_at=NOW + timedelta(hours=1))
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW + timedelta(days=1))

    offers = side_quests.catch_up(db, hunter, now=NOW + timedelta(days=1))

    assert offers == []
    assert side_quest.is_open(NOW + timedelta(days=1)) is False


def test_catching_up_respects_the_frequency_cap(db, hunter) -> None:
    """Opting in during a busy week does not dump six side quests on someone."""
    for i in range(6):
        broadcast_now(db, title=f"Trial {i}", now=NOW + timedelta(hours=i))

    side_quests.set_preference(
        db, hunter, is_opted_in=True, frequency=SideQuestFrequency.OCCASIONAL,
        now=NOW + timedelta(days=1),
    )
    offers = side_quests.catch_up(db, hunter, now=NOW + timedelta(days=1))

    assert len(offers) == 3


def test_opting_out_stops_new_offers(db, hunter) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quests.set_preference(db, hunter, is_opted_in=False, now=NOW)

    _, result = broadcast_now(db)

    assert result.offered_count == 0


def test_auto_accept_skips_the_question(db, hunter) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, auto_accept=True, now=NOW)

    broadcast_now(db)

    offer = side_quests.list_offers(db, hunter)[0]
    assert offer.status is SideQuestOfferStatus.ACCEPTED
    assert as_utc(offer.responded_at) == NOW


# --------------------------------------------------------------------------
# Dispatch scheduling
# --------------------------------------------------------------------------


def test_a_scheduled_broadcast_waits_for_its_moment(db, hunter) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quests.create_side_quest(
        db, title="Tomorrow's trial", broadcast_at=NOW + timedelta(days=1), now=NOW
    )

    assert side_quests.dispatch_due(db, now=NOW) == []
    assert len(side_quests.dispatch_due(db, now=NOW + timedelta(days=1))) == 1
    assert len(side_quests.list_offers(db, hunter)) == 1


def test_a_draft_is_never_dispatched(db, hunter) -> None:
    """Writing ahead must not put anything in front of a player."""
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quests.create_side_quest(
        db, title="Not ready yet", draft=True, broadcast_at=NOW, now=NOW
    )

    assert side_quests.dispatch_due(db, now=NOW + timedelta(days=1)) == []
    assert side_quests.list_offers(db, hunter) == []


def test_a_broadcast_that_slept_through_its_window_is_closed_not_sent(db, hunter) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quest = side_quests.create_side_quest(
        db,
        title="Missed entirely",
        broadcast_at=NOW,
        expires_at=NOW + timedelta(hours=1),
        now=NOW,
    )

    results = side_quests.dispatch_due(db, now=NOW + timedelta(days=1))

    assert results == []
    assert side_quest.status is SideQuestStatus.CLOSED
    assert side_quests.list_offers(db, hunter) == []


def test_a_cancelled_broadcast_cannot_go_out(db, hunter, settings) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quest, _ = broadcast_now(db)
    side_quests.cancel_side_quest(db, side_quest, settings, now=NOW)

    from app.errors import ValidationError

    with pytest.raises(ValidationError):
        side_quests.broadcast(db, side_quest, now=NOW)


def test_cancelling_voids_live_offers_without_penalty(db, hunter, settings) -> None:
    side_quests.set_preference(db, hunter, is_opted_in=True, now=NOW)
    side_quest, _ = broadcast_now(db, penalty_exp=500)
    offer = side_quests.list_offers(db, hunter)[0]
    side_quests.accept_offer(db, hunter, offer, now=NOW)

    voided = side_quests.cancel_side_quest(db, side_quest, settings, now=NOW)

    assert voided == 1
    assert offer.status is SideQuestOfferStatus.WITHDRAWN
    assert hunter.exp == 0
