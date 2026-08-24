"""The pure story rules: standing bands, favor math, and voice fallbacks."""

import pytest

from app.content.pantheon import SYSTEM_VOICE
from app.models.enums import (
    MAX_FAVOR,
    MIN_FAVOR,
    QuestDifficulty,
    SideQuestOfferStatus,
    Standing,
)
from app.services import story

# --------------------------------------------------------------------------
# Standing bands
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("favor", "expected"),
    [
        (-100, Standing.FORSAKEN),
        (-21, Standing.FORSAKEN),
        (-20, Standing.SLIGHTED),
        (-1, Standing.SLIGHTED),
        (0, Standing.STRANGER),
        (9, Standing.STRANGER),
        (10, Standing.NOTICED),
        (29, Standing.NOTICED),
        (30, Standing.FAVORED),
        (74, Standing.FAVORED),
        (75, Standing.CHAMPION),
        (100, Standing.CHAMPION),
    ],
)
def test_standing_bands(favor, expected) -> None:
    assert story.standing_for(favor) is expected


def test_everyone_starts_a_stranger() -> None:
    """Zero favor is the band a player who has never been offered anything is in."""
    assert story.standing_for(0) is Standing.STRANGER


def test_favor_is_bounded_in_both_directions() -> None:
    """Bounded so a long history never puts a change of behaviour out of reach."""
    assert story.clamp_favor(500) == MAX_FAVOR
    assert story.clamp_favor(-500) == MIN_FAVOR


@pytest.mark.parametrize(
    ("standing", "required", "allowed"),
    [
        (Standing.STRANGER, None, True),
        (Standing.STRANGER, Standing.NOTICED, False),
        (Standing.NOTICED, Standing.NOTICED, True),
        (Standing.CHAMPION, Standing.NOTICED, True),
        (Standing.FORSAKEN, Standing.STRANGER, False),
    ],
)
def test_standing_requirements(standing, required, allowed) -> None:
    assert story.meets_standing(standing, required) is allowed


# --------------------------------------------------------------------------
# What an ending is worth
# --------------------------------------------------------------------------


def test_clearing_a_harder_trial_is_worth_more() -> None:
    easy = story.favor_delta(SideQuestOfferStatus.COMPLETED, QuestDifficulty.E)
    hard = story.favor_delta(SideQuestOfferStatus.COMPLETED, QuestDifficulty.S)

    assert 0 < easy < hard


def test_abandoning_a_harder_trial_costs_more() -> None:
    easy = story.favor_delta(SideQuestOfferStatus.FAILED, QuestDifficulty.E)
    hard = story.favor_delta(SideQuestOfferStatus.FAILED, QuestDifficulty.S)

    assert hard < easy < 0


def test_declining_costs_less_than_ignoring() -> None:
    """Saying no is allowed. Leaving it hanging is what a constellation minds."""
    declined = story.favor_delta(SideQuestOfferStatus.DECLINED, QuestDifficulty.C)
    expired = story.favor_delta(SideQuestOfferStatus.EXPIRED, QuestDifficulty.C)

    assert expired < declined < 0


def test_declining_costs_the_same_whatever_the_rank() -> None:
    """You are passing on the interruption, not on the difficulty."""
    ranks = [story.favor_delta(SideQuestOfferStatus.DECLINED, d) for d in QuestDifficulty]

    assert len(set(ranks)) == 1


@pytest.mark.parametrize(
    "status", [SideQuestOfferStatus.OFFERED, SideQuestOfferStatus.ACCEPTED,
               SideQuestOfferStatus.WITHDRAWN],
)
def test_unsettled_and_withdrawn_endings_move_nothing(status) -> None:
    """An open offer has not been answered, and a withdrawal was not your doing."""
    assert story.favor_delta(status, QuestDifficulty.S) == 0


def test_declining_everything_cannot_reach_the_floor_quickly() -> None:
    """Sanity: a player who says no to fifty trials is slighted, not forsaken."""
    favor = 0
    for _ in range(50):
        favor = story.clamp_favor(
            favor + story.favor_delta(SideQuestOfferStatus.DECLINED, QuestDifficulty.C)
        )

    assert favor == -50
    assert story.standing_for(favor) is Standing.FORSAKEN


# --------------------------------------------------------------------------
# Which line gets said
# --------------------------------------------------------------------------


VOICE = {
    "offer": {"default": ["Get up."], "favored": ["You again. Get up."]},
    "complete": {"default": ["Good.", "Again."]},
}


def test_a_standing_specific_line_wins() -> None:
    assert story.pick_line("offer", Standing.FAVORED, voice=VOICE) == "You again. Get up."


def test_a_standing_with_no_line_falls_back_to_default() -> None:
    assert story.pick_line("offer", Standing.STRANGER, voice=VOICE) == "Get up."


def test_a_broadcast_line_beats_the_constellation(  ) -> None:
    overrides = {"offer": {"default": ["This one is different."]}}

    assert story.pick_line(
        "offer", Standing.FAVORED, overrides=overrides, voice=VOICE
    ) == "This one is different."


def test_a_kind_the_voice_has_no_answer_for_falls_through_to_the_system() -> None:
    """A half-written voice degrades to the System's register, never to silence."""
    line = story.pick_line("fail", Standing.STRANGER, voice=VOICE, fallback=SYSTEM_VOICE)

    assert line == SYSTEM_VOICE["fail"]["default"][0]


def test_nothing_anywhere_returns_none() -> None:
    assert story.pick_line("fail", Standing.STRANGER, voice=VOICE) is None


def test_the_same_seed_always_reads_the_same_way() -> None:
    """A feed re-rendered must not reword itself."""
    first = story.pick_line("complete", Standing.STRANGER, voice=VOICE, seed=7)
    again = story.pick_line("complete", Standing.STRANGER, voice=VOICE, seed=7)

    assert first == again


def test_different_seeds_reach_different_alternatives() -> None:
    lines = {
        story.pick_line("complete", Standing.STRANGER, voice=VOICE, seed=seed)
        for seed in range(4)
    }

    assert lines == {"Good.", "Again."}


def test_a_malformed_voice_does_not_raise() -> None:
    """Content is hand-written; a typo should degrade, not 500."""
    assert story.pick_line("offer", Standing.STRANGER, voice={"offer": "Get up."}) is None
