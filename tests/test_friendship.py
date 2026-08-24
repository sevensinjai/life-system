"""Asking to be befriended: the roll, the trial, and the wait."""

import random
from datetime import UTC, datetime, timedelta

import pytest

from app.content.challenges import CHALLENGES
from app.errors import ValidationError
from app.models import (
    EventType,
    FriendshipRequest,
    FriendshipStatus,
    Player,
    SideQuestOfferStatus,
    SystemEvent,
    User,
)
from app.security import hash_password
from app.services import constellations, friendship, side_quests
from app.services.clock import as_utc
from app.services.friendship import ChanceArbiter, Petition, Verdict

NOW = datetime(2026, 8, 24, 12, tzinfo=UTC)


def hears(petition: Petition) -> Verdict:
    """An arbiter that always agrees to hear a request."""
    return Verdict(heard=True, reason="Heard.")


def deaf(petition: Petition) -> Verdict:
    """An arbiter that never does."""
    return Verdict(heard=False, reason="Not heard.")


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
def star(db):
    constellations.seed_pantheon(db)
    return constellations.get_by_code(db, "xingtian")


def ask(db, hunter, star, settings, *, arbiter=hears, now=NOW, message=None):
    return friendship.request_friendship(
        db, hunter, star, settings, message=message, arbiter=arbiter, now=now
    )


def clear_the_trial(db, hunter, request, settings, *, now=NOW):
    """Accept and complete the trial of admission a request set."""
    offer = side_quests.get_offer(db, hunter, request.challenge_offer_id)
    side_quests.accept_offer(db, hunter, offer, now=now)
    side_quests.complete_offer(db, hunter, offer, settings, now=now)
    return offer


# --------------------------------------------------------------------------
# Being heard, or not
# --------------------------------------------------------------------------


def test_a_refusal_is_an_answer_not_an_error(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings, arbiter=deaf)

    assert request.status is FriendshipStatus.REFUSED
    assert request.challenge_offer_id is None
    assert constellations.get_favor(db, hunter, star).is_friend is False


def test_being_heard_sets_a_trial(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)

    assert request.status is FriendshipStatus.CHALLENGED
    offer = side_quests.get_offer(db, hunter, request.challenge_offer_id)
    assert offer.side_quest.is_challenge is True
    assert offer.side_quest.catalog_code == CHALLENGES["xingtian"].code


def test_the_trial_is_not_yet_friendship(db, hunter, star, settings) -> None:
    ask(db, hunter, star, settings)

    assert constellations.get_favor(db, hunter, star).is_friend is False


def test_clearing_the_trial_makes_you_friends(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)

    clear_the_trial(db, hunter, request, settings)

    assert request.status is FriendshipStatus.ACCEPTED
    favor = constellations.get_favor(db, hunter, star)
    assert favor.is_friend is True
    assert favor.befriended_at is not None


def test_what_the_player_wrote_is_kept(db, hunter, star, settings) -> None:
    """Nothing weighs it yet; it is kept for whatever eventually does."""
    request = ask(db, hunter, star, settings, message="  I fell too.  ")

    assert request.message == "I fell too."


def test_an_overlong_message_is_refused(db, hunter, star, settings) -> None:
    with pytest.raises(ValidationError, match="at most"):
        ask(db, hunter, star, settings, message="x" * 1001)


# --------------------------------------------------------------------------
# Failing the trial
# --------------------------------------------------------------------------


def test_letting_the_trial_lapse_closes_the_request(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)

    side_quests.sweep_offers(db, hunter, settings, now=NOW + timedelta(days=3))

    assert request.status is FriendshipStatus.FAILED
    assert constellations.get_favor(db, hunter, star).is_friend is False


def test_declining_the_trial_closes_the_request(db, hunter, star, settings) -> None:
    """Changing your mind about asking is a thing people do."""
    request = ask(db, hunter, star, settings)
    offer = side_quests.get_offer(db, hunter, request.challenge_offer_id)

    side_quests.decline_offer(db, hunter, offer, settings, now=NOW)

    assert request.status is FriendshipStatus.FAILED


def test_abandoning_the_trial_closes_the_request(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    offer = side_quests.get_offer(db, hunter, request.challenge_offer_id)
    side_quests.accept_offer(db, hunter, offer, now=NOW)

    side_quests.sweep_offers(db, hunter, settings, now=NOW + timedelta(days=3))

    assert offer.status is SideQuestOfferStatus.FAILED
    assert request.status is FriendshipStatus.FAILED


def test_a_failed_trial_costs_no_exp(db, hunter, star, settings) -> None:
    """A stranger who fails an audition has lost the audition. That is enough."""
    hunter.exp = 200
    request = ask(db, hunter, star, settings)
    offer = side_quests.get_offer(db, hunter, request.challenge_offer_id)
    side_quests.accept_offer(db, hunter, offer, now=NOW)

    side_quests.sweep_offers(db, hunter, settings, now=NOW + timedelta(days=3))

    assert hunter.exp == 200


def test_a_withdrawn_trial_starts_no_wait(db, hunter, star, settings) -> None:
    """The constellation called it off; that is not the player's fault."""
    request = ask(db, hunter, star, settings)
    offer = side_quests.get_offer(db, hunter, request.challenge_offer_id)

    side_quests.cancel_side_quest(db, offer.side_quest, settings, now=NOW)

    assert request.status is FriendshipStatus.WITHDRAWN
    assert friendship.retry_at(db, hunter, star) is None
    assert friendship.may_ask(db, hunter, star, NOW) == (True, None)


# --------------------------------------------------------------------------
# The wait
# --------------------------------------------------------------------------


def test_a_refusal_starts_a_seven_day_wait(db, hunter, star, settings) -> None:
    ask(db, hunter, star, settings, arbiter=deaf)

    assert as_utc(friendship.retry_at(db, hunter, star)) == NOW + timedelta(
        days=settings.friendship_retry_days
    )


def test_asking_again_inside_the_wait_is_refused(db, hunter, star, settings) -> None:
    ask(db, hunter, star, settings, arbiter=deaf)

    with pytest.raises(ValidationError, match="will not hear you again yet"):
        ask(db, hunter, star, settings, now=NOW + timedelta(days=6))


def test_asking_again_after_the_wait_is_allowed(db, hunter, star, settings) -> None:
    ask(db, hunter, star, settings, arbiter=deaf)

    later = NOW + timedelta(days=8)
    request = ask(db, hunter, star, settings, now=later)

    assert request.status is FriendshipStatus.CHALLENGED


def test_a_failed_trial_starts_the_same_wait(db, hunter, star, settings) -> None:
    ask(db, hunter, star, settings)
    side_quests.sweep_offers(db, hunter, settings, now=NOW + timedelta(days=3))

    assert as_utc(friendship.retry_at(db, hunter, star)) == NOW + timedelta(
        days=3 + settings.friendship_retry_days
    )
    with pytest.raises(ValidationError, match="will not hear you again yet"):
        ask(db, hunter, star, settings, now=NOW + timedelta(days=4))


def test_a_second_request_while_one_is_open_is_refused(db, hunter, star, settings) -> None:
    ask(db, hunter, star, settings)

    with pytest.raises(ValidationError, match="already set you a trial"):
        ask(db, hunter, star, settings)


def test_asking_a_friend_is_refused(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    clear_the_trial(db, hunter, request, settings)

    with pytest.raises(ValidationError, match="already your friend"):
        ask(db, hunter, star, settings)


def test_the_wait_is_per_constellation(db, hunter, star, settings) -> None:
    """Being turned away by one says nothing about the others."""
    ask(db, hunter, star, settings, arbiter=deaf)
    road = constellations.get_by_code(db, "hermes")

    request = friendship.request_friendship(
        db, hunter, road, settings, arbiter=hears, now=NOW
    )

    assert request.status is FriendshipStatus.CHALLENGED


def test_every_request_is_kept(db, hunter, star, settings) -> None:
    ask(db, hunter, star, settings, arbiter=deaf)
    ask(db, hunter, star, settings, arbiter=deaf, now=NOW + timedelta(days=8))
    ask(db, hunter, star, settings, now=NOW + timedelta(days=16))
    db.flush()

    assert db.query(FriendshipRequest).count() == 3


# --------------------------------------------------------------------------
# What friendship opens
# --------------------------------------------------------------------------


def test_a_stranger_receives_nothing(db, hunter, star, settings) -> None:
    side_quest = side_quests.create_side_quest(
        db, title="A trial", constellation=star, expires_at=NOW + timedelta(days=2),
        now=NOW,
    )

    result = side_quests.broadcast(db, side_quest, now=NOW)

    assert result.offered_count == 0
    assert result.skipped == {"not_a_friend": 1}


def test_a_friend_receives(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    clear_the_trial(db, hunter, request, settings)

    side_quest = side_quests.create_side_quest(
        db, title="A trial", constellation=star, expires_at=NOW + timedelta(days=2),
        now=NOW,
    )
    result = side_quests.broadcast(db, side_quest, now=NOW)

    assert result.offered_count == 1


def test_the_system_itself_still_reaches_everyone(db, hunter, settings) -> None:
    """A broadcast with nobody behind it has no friendship to check."""
    side_quest = side_quests.create_side_quest(
        db, title="From the System", expires_at=NOW + timedelta(days=2), now=NOW
    )

    result = side_quests.broadcast(db, side_quest, now=NOW)

    assert result.offered_count == 1


def test_ending_a_friendship_closes_the_channel(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    clear_the_trial(db, hunter, request, settings)

    friendship.end_friendship(db, hunter, star, settings, now=NOW)

    side_quest = side_quests.create_side_quest(
        db, title="A trial", constellation=star, expires_at=NOW + timedelta(days=2),
        now=NOW,
    )
    assert side_quests.broadcast(db, side_quest, now=NOW).offered_count == 0


def test_ending_a_friendship_keeps_the_standing(db, hunter, star, settings) -> None:
    """The history happened. Walking away does not unmake it."""
    request = ask(db, hunter, star, settings)
    clear_the_trial(db, hunter, request, settings)
    favor_before = constellations.get_favor(db, hunter, star).favor

    friendship.end_friendship(db, hunter, star, settings, now=NOW)

    assert constellations.get_favor(db, hunter, star).favor == favor_before


def test_coming_back_waits_out_the_same_period(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    clear_the_trial(db, hunter, request, settings)
    friendship.end_friendship(db, hunter, star, settings, now=NOW)

    with pytest.raises(ValidationError, match="will not hear you again yet"):
        ask(db, hunter, star, settings, now=NOW + timedelta(days=1))

    assert friendship.may_ask(db, hunter, star, NOW + timedelta(days=8))[0] is True


def test_ending_what_was_never_started_is_refused(db, hunter, star, settings) -> None:
    with pytest.raises(ValidationError, match="not your friend"):
        friendship.end_friendship(db, hunter, star, settings, now=NOW)


# --------------------------------------------------------------------------
# The trial is asked for, so it is not an interruption
# --------------------------------------------------------------------------


def test_a_trial_of_admission_ignores_the_weekly_cap(db, hunter, star, settings) -> None:
    """You asked for this one; it must not eat the week you rationed."""
    side_quests.set_preference(db, hunter, frequency="rare", now=NOW)

    ask(db, hunter, star, settings)

    assert side_quests.offers_in_window(db, hunter, NOW) == 0


def test_a_trial_of_admission_is_never_broadcast(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    offer = side_quests.get_offer(db, hunter, request.challenge_offer_id)

    with pytest.raises(ValidationError, match="cannot be broadcast"):
        side_quests.broadcast(db, offer.side_quest, now=NOW)


def test_someone_elses_trial_is_not_an_open_broadcast(db, hunter, star, settings) -> None:
    """Catching up on what is open must not hand over another player's audition."""
    ask(db, hunter, star, settings)

    user = User(email="other@example.com", hashed_password=hash_password("x" * 12))
    db.add(user)
    db.flush()
    other = Player(user_id=user.id, name="Cha Hae-In", timezone="UTC")
    db.add(other)
    db.flush()
    side_quests.set_preference(db, other, is_opted_in=True, now=NOW)

    assert side_quests.catch_up(db, other, now=NOW) == []


def test_a_pending_trial_does_not_keep_the_sky_quiet(db, hunter, star, settings) -> None:
    from app.services import broadcasting

    ask(db, hunter, star, settings)

    assert broadcasting.has_open_broadcast(db, now=NOW) is False


# --------------------------------------------------------------------------
# The arbiter
# --------------------------------------------------------------------------


def test_the_chance_arbiter_hears_about_the_configured_share() -> None:
    arbiter = ChanceArbiter(rate=0.30, rng=random.Random(20260824))

    heard = sum(arbiter(None).heard for _ in range(2000))

    assert 0.27 <= heard / 2000 <= 0.33


def test_the_chance_arbiter_reads_nothing() -> None:
    """It is a placeholder. It takes the petition and ignores it, by design."""
    arbiter = ChanceArbiter(rate=1.0, rng=random.Random(1))

    assert arbiter(None).heard is True


def test_the_arbiters_reason_is_kept_on_the_request(db, hunter, star, settings) -> None:
    """Where an arbiter that explains itself will put its words."""

    def opinionated(petition: Petition) -> Verdict:
        return Verdict(heard=False, reason="You have not earned this.")

    request = ask(db, hunter, star, settings, arbiter=opinionated)

    assert request.verdict_reason == "You have not earned this."


def test_the_petition_carries_what_a_reading_arbiter_would_need(
    db, hunter, star, settings
) -> None:
    seen: list[Petition] = []

    def nosy(petition: Petition) -> Verdict:
        seen.append(petition)
        return Verdict(heard=False)

    ask(db, hunter, star, settings, arbiter=nosy, message="Please.")

    petition = seen[0]
    assert petition.player is hunter
    assert petition.constellation is star
    assert petition.message == "Please."
    assert petition.previous_requests == 0
    assert petition.standing.value == "stranger"


# --------------------------------------------------------------------------
# The feed
# --------------------------------------------------------------------------


def test_a_refusal_is_spoken_in_the_constellations_voice(
    db, hunter, star, settings
) -> None:
    ask(db, hunter, star, settings, arbiter=deaf)
    db.flush()

    event = (
        db.query(SystemEvent)
        .filter_by(player_id=hunter.id, event_type=EventType.FRIENDSHIP_REFUSED)
        .one()
    )
    assert event.message.startswith("The Will That Remains: ")
    assert event.payload["retry_after"] is not None


def test_being_befriended_is_announced(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    clear_the_trial(db, hunter, request, settings)
    db.flush()

    event = (
        db.query(SystemEvent)
        .filter_by(player_id=hunter.id, event_type=EventType.FRIENDSHIP_FORMED)
        .one()
    )
    assert "of my company" in event.message


def test_a_farewell_is_spoken(db, hunter, star, settings) -> None:
    request = ask(db, hunter, star, settings)
    clear_the_trial(db, hunter, request, settings)
    friendship.end_friendship(db, hunter, star, settings, now=NOW)
    db.flush()

    event = (
        db.query(SystemEvent)
        .filter_by(player_id=hunter.id, event_type=EventType.FRIENDSHIP_ENDED)
        .one()
    )
    assert event.payload["constellation"] == "xingtian"


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------


def test_every_constellation_has_a_trial_of_admission(db) -> None:
    """Without one, a constellation could never be befriended at all."""
    constellations.seed_pantheon(db)

    for constellation in constellations.list_constellations(db):
        assert CHALLENGES.get(constellation.code) is not None, constellation.code


def test_no_trial_of_admission_carries_a_penalty() -> None:
    assert all(entry.penalty_exp == 0 for entry in CHALLENGES.values())
