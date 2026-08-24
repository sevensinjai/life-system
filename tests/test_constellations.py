"""The pantheon in play: seeding, regard, gated trials, and the API."""

from datetime import UTC, datetime, timedelta

import pytest

from app.content.broadcasts import BROADCASTS
from app.content.broadcasts import by_code as broadcasts_by_code
from app.content.broadcasts import for_constellation as broadcasts_for
from app.content.pantheon import PANTHEON
from app.content.pantheon import by_code as pantheon_by_code
from app.models import (
    Constellation,
    ConstellationFavor,
    EventType,
    Player,
    QuestDifficulty,
    SideQuestOfferStatus,
    Standing,
    SystemEvent,
    User,
)
from app.models.enums import MythTradition, StatName
from app.security import hash_password
from app.services import broadcasting, constellations, side_quests, story
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
def pantheon(db, hunter) -> dict[str, Constellation]:
    """The seeded pantheon, all of them already friends with the player.

    A constellation reaches its friends and nobody else, so tests about what
    it *sends* start from friendship; tests about getting in live in
    tests/test_friendship.py.
    """
    constellations.seed_pantheon(db)
    found = {c.code: c for c in constellations.list_constellations(db)}
    for constellation in found.values():
        befriend(db, hunter, constellation, when=NOW)
    return found


def issue(db, constellation, *, difficulty=QuestDifficulty.C, **kwargs):
    """Broadcast one trial from a constellation and return the player's offer."""
    kwargs.setdefault("title", "A trial")
    kwargs.setdefault("expires_at", DEADLINE)
    side_quest = side_quests.create_side_quest(
        db, constellation=constellation, difficulty=difficulty, now=NOW, **kwargs
    )
    side_quests.broadcast(db, side_quest, now=NOW)
    return side_quest


# --------------------------------------------------------------------------
# Seeding
# --------------------------------------------------------------------------


def test_seeding_loads_the_written_pantheon(db) -> None:
    result = constellations.seed_pantheon(db)

    assert result.created_count == len(PANTHEON)
    assert {c.code for c in constellations.list_constellations(db)} == set(
        pantheon_by_code()
    )


def test_seeding_twice_changes_nothing(db) -> None:
    constellations.seed_pantheon(db)

    again = constellations.seed_pantheon(db)

    assert again.created_count == 0
    assert again.updated_count == 0


def test_a_rewritten_voice_updates_in_place(db, hunter, pantheon) -> None:
    """A constellation must survive a rewrite with its history intact."""
    star = pantheon["xingtian"]
    constellations.record_outcome(
        db, hunter, star, SideQuestOfferStatus.COMPLETED, QuestDifficulty.C, now=NOW
    )
    favor_before = constellations.get_favor(db, hunter, star).favor

    entries = tuple(
        type(entry)(**{**entry.__dict__, "code_name": "The Star That Fell"})
        if entry.code == "xingtian"
        else entry
        for entry in PANTHEON
    )
    result = constellations.seed_pantheon(db, entries)

    assert result.updated == ["xingtian"]
    assert star.code_name == "The Star That Fell"
    assert constellations.get_favor(db, hunter, star).favor == favor_before


def test_a_constellation_that_leaves_the_catalog_is_retired_not_deleted(
    db, hunter
) -> None:
    """Recasting the pantheon must not delete anyone's history with the old one."""
    constellations.seed_pantheon(db)
    departing = constellations.get_by_code(db, "argus")
    befriend(db, hunter, departing, when=NOW)
    constellations.record_outcome(
        db, hunter, departing, SideQuestOfferStatus.COMPLETED, QuestDifficulty.C,
        now=NOW,
    )
    favor_before = constellations.get_favor(db, hunter, departing).favor

    remaining = tuple(entry for entry in PANTHEON if entry.code != "argus")
    result = constellations.seed_pantheon(db, remaining)

    assert result.retired == ["argus"]
    assert departing.is_active is False
    assert constellations.get_favor(db, hunter, departing).favor == favor_before
    # Retired means "issues nothing", not "gone": it is off the pantheon list
    # but still resolvable by code, so old events can still be rendered.
    assert departing not in constellations.list_constellations(db)
    assert constellations.get_by_code(db, "argus") is departing


def test_a_retired_constellation_stops_reaching_its_friends(db, hunter, settings) -> None:
    constellations.seed_pantheon(db)
    departing = constellations.get_by_code(db, "argus")
    befriend(db, hunter, departing, when=NOW)
    constellations.seed_pantheon(
        db, tuple(entry for entry in PANTHEON if entry.code != "argus")
    )

    side_quest = side_quests.create_side_quest(
        db, title="A last look", constellation=departing, expires_at=DEADLINE, now=NOW
    )

    assert side_quests.broadcast(db, side_quest, now=NOW).offered_count == 0


def test_a_constellation_that_returns_is_reinstated(db) -> None:
    constellations.seed_pantheon(db)
    without = tuple(entry for entry in PANTHEON if entry.code != "argus")
    constellations.seed_pantheon(db, without)

    constellations.seed_pantheon(db)

    assert constellations.get_by_code(db, "argus").is_active is True


def test_every_written_trial_belongs_to_a_real_constellation() -> None:
    """The catalogs are hand-written; nothing checks them but this."""
    known = set(pantheon_by_code())

    assert {entry.constellation for entry in BROADCASTS} <= known


def test_every_constellation_has_something_to_send() -> None:
    """One with no trials could be befriended and then never speak again."""
    for entry in PANTHEON:
        assert broadcasts_for(entry.code), entry.code


def test_the_pantheon_spans_every_tradition() -> None:
    found = {entry.tradition for entry in PANTHEON}

    assert found == set(MythTradition)


def test_every_stat_has_a_constellation_that_cares_about_it() -> None:
    """A player who wants to raise one stat must have somewhere to go for it."""
    claimed = {entry.domain for entry in PANTHEON if entry.domain}

    assert claimed == set(StatName)


def test_some_constellations_care_about_the_habit_rather_than_a_stat() -> None:
    assert any(entry.domain is None for entry in PANTHEON)


def test_codes_are_unique() -> None:
    assert len(pantheon_by_code()) == len(PANTHEON)


def test_every_constellation_says_something_of_its_own() -> None:
    """A silent voice would fall all the way through to the System register."""
    for entry in PANTHEON:
        assert entry.voice, entry.code
        # The moments that carry the relationship: being sent something,
        # clearing it, being turned away, and being taken in.
        for kind in ("offer", "complete", "refuse", "befriend"):
            assert kind in entry.voice, f"{entry.code}: {kind}"


def test_every_constellation_is_described() -> None:
    """The description is the only place the actual myth gets told."""
    for entry in PANTHEON:
        assert len(entry.description) > 120, entry.code


def test_written_trials_have_unique_codes() -> None:
    assert len(broadcasts_by_code()) == len(BROADCASTS)


def test_no_written_trial_costs_more_than_it_pays() -> None:
    """A side quest is an offer, not a debt."""
    for entry in BROADCASTS:
        reward = entry.exp_reward or side_quests.default_exp_for(entry.difficulty)
        assert entry.penalty_exp < reward, entry.code


# --------------------------------------------------------------------------
# Regard
# --------------------------------------------------------------------------


def test_two_who_have_never_met_leave_no_row(db, hunter) -> None:
    constellations.seed_pantheon(db)
    road = constellations.get_by_code(db, "hermes")

    favor = constellations.get_favor(db, hunter, road)

    assert favor.favor == 0
    assert favor.is_friend is False
    assert db.query(ConstellationFavor).count() == 0


def test_being_offered_something_starts_a_record(db, hunter, pantheon) -> None:
    issue(db, pantheon["xingtian"])

    favor = constellations.get_favor(db, hunter, pantheon["xingtian"])
    assert favor.offers_received == 1
    assert favor.favor == 0  # meeting is not yet an opinion
    assert favor.first_seen_at is not None


def test_clearing_trials_raises_standing(db, hunter, pantheon, settings) -> None:
    star = pantheon["xingtian"]
    for i in range(3):
        side_quest = side_quests.create_side_quest(
            db, title=f"Trial {i}", constellation=star, difficulty=QuestDifficulty.B,
            expires_at=DEADLINE, now=NOW,
        )
        side_quests.broadcast(db, side_quest, now=NOW + timedelta(hours=i))
        offer = side_quests.list_offers(db, hunter)[0]
        side_quests.accept_offer(db, hunter, offer, now=NOW)
        side_quests.complete_offer(db, hunter, offer, settings, now=NOW)

    favor = constellations.get_favor(db, hunter, star)
    assert favor.completed == 3
    assert story.standing_for(favor.favor) is Standing.NOTICED


def test_abandoning_a_trial_lowers_standing(db, hunter, pantheon, settings) -> None:
    star = pantheon["xingtian"]
    issue(db, star, difficulty=QuestDifficulty.A)
    offer = side_quests.list_offers(db, hunter)[0]
    side_quests.accept_offer(db, hunter, offer, now=NOW)

    side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    favor = constellations.get_favor(db, hunter, star)
    assert favor.failed == 1
    assert story.standing_for(favor.favor) is Standing.SLIGHTED


def test_standing_never_touches_exp(db, hunter, pantheon, settings) -> None:
    """A constellation's opinion is a story value. It cannot take anything."""
    hunter.exp = 300
    issue(db, pantheon["xingtian"], difficulty=QuestDifficulty.S, penalty_exp=0)
    offer = side_quests.list_offers(db, hunter)[0]
    side_quests.accept_offer(db, hunter, offer, now=NOW)

    side_quests.sweep_offers(db, hunter, settings, now=AFTER)

    assert constellations.get_favor(db, hunter, pantheon["xingtian"]).favor < 0
    assert hunter.exp == 300
    assert hunter.level == 1


def test_each_constellation_keeps_its_own_regard(db, hunter, pantheon, settings) -> None:
    issue(db, pantheon["xingtian"], title="Star's trial")
    star_offer = side_quests.list_offers(db, hunter)[0]
    side_quests.accept_offer(db, hunter, star_offer, now=NOW)
    side_quests.complete_offer(db, hunter, star_offer, settings, now=NOW)

    issue(db, pantheon["hermes"], title="Road's trial")
    road_offer = side_quests.list_offers(db, hunter)[0]
    side_quests.decline_offer(db, hunter, road_offer, settings, now=NOW)

    assert constellations.get_favor(db, hunter, pantheon["xingtian"]).favor > 0
    assert constellations.get_favor(db, hunter, pantheon["hermes"]).favor < 0


def test_a_withdrawn_trial_is_not_held_against_you(db, hunter, pantheon, settings) -> None:
    star = pantheon["xingtian"]
    side_quest = issue(db, star)
    offer = side_quests.list_offers(db, hunter)[0]
    side_quests.accept_offer(db, hunter, offer, now=NOW)

    side_quests.cancel_side_quest(db, side_quest, settings, now=NOW)

    assert constellations.get_favor(db, hunter, star).favor == 0


# --------------------------------------------------------------------------
# What standing changes
# --------------------------------------------------------------------------


def test_a_reserved_trial_skips_a_stranger(db, hunter, pantheon) -> None:
    side_quest = side_quests.create_side_quest(
        db, title="For those who have earned it", constellation=pantheon["xingtian"],
        min_standing=Standing.FAVORED, expires_at=DEADLINE, now=NOW,
    )

    result = side_quests.broadcast(db, side_quest, now=NOW)

    assert result.offered_count == 0
    assert result.skipped == {"standing_too_low": 1}


def test_a_reserved_trial_reaches_someone_who_earned_it(db, hunter, pantheon) -> None:
    star = pantheon["xingtian"]
    favor = constellations.ensure_favor(db, hunter, star)
    favor.favor = 40  # FAVORED

    side_quest = side_quests.create_side_quest(
        db, title="For those who have earned it", constellation=star,
        min_standing=Standing.FAVORED, expires_at=DEADLINE, now=NOW,
    )
    result = side_quests.broadcast(db, side_quest, now=NOW)

    assert result.offered_count == 1


def test_the_voice_changes_with_standing(db, hunter, pantheon, settings) -> None:
    """The same constellation should not greet a champion like a stranger."""
    star = pantheon["xingtian"]
    stranger_line = constellations.line_for(
        side_quests.create_side_quest(db, title="A", constellation=star, now=NOW),
        star, story.OFFER, Standing.STRANGER,
    )
    champion_line = constellations.line_for(
        side_quests.create_side_quest(db, title="B", constellation=star, now=NOW),
        star, story.OFFER, Standing.CHAMPION,
    )

    assert stranger_line != champion_line


def test_the_feed_carries_the_voice_and_the_facts(db, hunter, pantheon) -> None:
    issue(db, pantheon["amaterasu"], title="Come back once more")
    db.flush()

    event = (
        db.query(SystemEvent)
        .filter_by(player_id=hunter.id, event_type=EventType.SIDE_QUEST_OFFERED)
        .one()
    )
    assert event.message.startswith("The Door Opened Again: ")
    assert event.payload["constellation"] == "amaterasu"
    assert event.payload["standing"] == "stranger"
    assert event.payload["title"] == "Come back once more"


def test_a_completion_reports_how_regard_moved(db, hunter, pantheon, settings) -> None:
    """Clearing an S-rank is enough to move a stranger up a band in one go."""
    issue(db, pantheon["michizane"], difficulty=QuestDifficulty.S)
    offer = side_quests.list_offers(db, hunter)[0]
    side_quests.accept_offer(db, hunter, offer, now=NOW)
    side_quests.complete_offer(db, hunter, offer, settings, now=NOW)
    db.flush()

    event = (
        db.query(SystemEvent)
        .filter_by(player_id=hunter.id, event_type=EventType.SIDE_QUEST_COMPLETED)
        .one()
    )
    assert event.payload["favor_delta"] > 0
    assert event.payload["standing_changed"] is True
    assert "EXP" in event.message


def test_a_broadcast_with_nobody_behind_it_still_speaks(db, hunter) -> None:
    """The System's own register is the fallback, not silence."""
    side_quest = side_quests.create_side_quest(
        db, title="From the System itself", expires_at=DEADLINE, now=NOW
    )
    side_quests.broadcast(db, side_quest, now=NOW)
    db.flush()

    event = (
        db.query(SystemEvent)
        .filter_by(player_id=hunter.id, event_type=EventType.SIDE_QUEST_OFFERED)
        .one()
    )
    assert event.message == "A side quest has been issued."
    assert event.payload["constellation"] is None


# --------------------------------------------------------------------------
# Scheduling from the catalog
# --------------------------------------------------------------------------


def test_the_scheduler_starts_at_the_top_of_the_catalog(db, pantheon) -> None:
    scheduled = broadcasting.schedule_next(db, now=NOW)

    assert scheduled is not None
    assert scheduled.entry.code == BROADCASTS[0].code
    assert scheduled.side_quest.catalog_code == BROADCASTS[0].code


def test_a_scheduled_trial_carries_its_constellation_and_window(db, pantheon) -> None:
    scheduled = broadcasting.schedule(
        db, broadcasting.entry_by_code("yan_hui.eight_glasses"), at=NOW, now=NOW
    )

    assert scheduled.side_quest.constellation.code == "yan_hui"
    assert scheduled.side_quest.expires_at == NOW + timedelta(hours=24)


def spend_the_catalog(db, *, now=NOW) -> list[str]:
    """Send every written trial once, at one instant so none of them rests."""
    sent = []
    for _ in range(len(BROADCASTS)):
        scheduled = broadcasting.schedule_next(db, now=now)
        assert scheduled is not None
        sent.append(scheduled.entry.code)
    return sent


def test_the_rotation_does_not_repeat_before_the_catalog_is_spent(db, pantheon) -> None:
    """Everything written gets seen before anything is seen twice."""
    sent = spend_the_catalog(db)

    assert len(set(sent)) == len(BROADCASTS)


def test_a_spent_catalog_rests_rather_than_repeating(db, pantheon) -> None:
    spend_the_catalog(db)

    assert broadcasting.schedule_next(db, now=NOW) is None


def test_a_rested_trial_comes_round_again(db, pantheon) -> None:
    spend_the_catalog(db)

    later = NOW + timedelta(days=broadcasting.COOLDOWN_DAYS + 1)
    scheduled = broadcasting.schedule_next(db, now=later)

    assert scheduled is not None
    assert scheduled.entry.code == BROADCASTS[0].code  # the longest-waiting one


def test_the_catalog_outlasts_the_cooldown(db, pantheon) -> None:
    """A trial should not come round again while unsent ones are waiting.

    True only while the catalog is longer than the cooldown can absorb, which
    is a property of the written content rather than of the code — so it is
    checked here, where growing the catalog cannot quietly break it.
    """
    assert len(BROADCASTS) > broadcasting.COOLDOWN_DAYS


def test_scheduling_a_trial_whose_constellation_is_missing_is_refused(db) -> None:
    """Better a clear error than a broadcast from nobody."""
    from app.errors import ValidationError

    with pytest.raises(ValidationError, match="seed it"):
        broadcasting.schedule(db, BROADCASTS[0], at=NOW, now=NOW)


def test_the_sky_reports_when_something_is_already_out(db, pantheon) -> None:
    assert broadcasting.has_open_broadcast(db, now=NOW) is False

    broadcasting.schedule_next(db, at=NOW, now=NOW)

    assert broadcasting.has_open_broadcast(db, now=NOW) is True


# --------------------------------------------------------------------------
# The API
# --------------------------------------------------------------------------


def test_the_pantheon_lists_with_your_standing(auth_client, db) -> None:
    constellations.seed_pantheon(db)
    db.commit()

    body = auth_client.get("/constellations").json()

    assert len(body) == len(PANTHEON)
    assert body[0]["standing"]["standing"] == "stranger"
    assert body[0]["standing"]["offers_received"] == 0


def test_the_pantheon_can_be_read_one_tradition_at_a_time(auth_client, db) -> None:
    """Twenty-six is too many to read as one list."""
    constellations.seed_pantheon(db)
    db.commit()

    body = auth_client.get("/constellations?tradition=japanese").json()

    assert body
    assert {entry["tradition"] for entry in body} == {"japanese"}
    assert len(body) < len(PANTHEON)


def test_looking_at_the_pantheon_creates_no_history(auth_client, db) -> None:
    constellations.seed_pantheon(db)
    db.commit()

    auth_client.get("/constellations")

    assert db.query(ConstellationFavor).count() == 0


def test_one_constellation_by_code(auth_client, db) -> None:
    """Both names, in both scripts, so the client picks — or shows both."""
    constellations.seed_pantheon(db)
    db.commit()

    body = auth_client.get("/constellations/yan_hui").json()

    assert body["code_name"] == "One Basket, One Gourd"
    assert body["code_name_zh_hant"] == "「一簞一瓢」"
    assert body["real_name"] == "Yan Hui"
    assert body["real_name_zh_hant"] == "顏回"
    assert body["domain"] == "vitality"


def test_every_constellation_is_named_in_both_scripts(db) -> None:
    """A half-translated pantheon would render as a gap on a Chinese client."""
    constellations.seed_pantheon(db)

    for constellation in constellations.list_constellations(db):
        assert constellation.code_name, constellation.code
        assert constellation.code_name_zh_hant, constellation.code
        assert constellation.real_name, constellation.code
        assert constellation.real_name_zh_hant, constellation.code
        assert constellation.epithet_zh_hant, constellation.code


def test_names_are_distinct_across_the_pantheon(db) -> None:
    """Two constellations sharing a name would be a content typo, not a design."""
    constellations.seed_pantheon(db)
    found = constellations.list_constellations(db)

    for field in ("code_name", "code_name_zh_hant", "real_name", "real_name_zh_hant"):
        values = [getattr(c, field) for c in found]
        assert len(set(values)) == len(values), field


def test_a_renamed_constellation_keeps_its_history(db, hunter) -> None:
    """The code is the identity; the names are content, and content changes."""
    constellations.seed_pantheon(db)
    star = constellations.get_by_code(db, "xingtian")
    befriend(db, hunter, star, when=NOW)

    entries = tuple(
        type(entry)(**{**entry.__dict__, "real_name_zh_hant": "刑天氏"})
        if entry.code == "xingtian"
        else entry
        for entry in PANTHEON
    )
    constellations.seed_pantheon(db, entries)

    assert star.real_name_zh_hant == "刑天氏"
    assert constellations.get_favor(db, hunter, star).is_friend is True


def test_an_unknown_code_is_a_404(auth_client, db) -> None:
    constellations.seed_pantheon(db)
    db.commit()

    response = auth_client.get("/constellations/the_absent_one")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
