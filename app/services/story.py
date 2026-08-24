"""Standing, favor, and which line a constellation says.

Pure by design — no ORM, no session, no clock — the same way `leveling` and
`scheduling` are. Everything here is a function of its arguments, which is
what makes the favor curve and the voice fallbacks cheap to test and safe to
retune.

Two things live here:

**Favor**, the running score one constellation keeps on one player, and the
*standing* band that score falls into. Favor moves on what the player did with
what they were offered, and it never touches EXP, levels, or stats — a
constellation's opinion is a story value, not a punishment.

**Voice**, the resolution of "what does this constellation say when X
happens?" — a broadcast's own line if it has one, else the constellation's
line for that standing, else its default, else the plain System line.
"""

from app.models.enums import (
    MAX_FAVOR,
    MIN_FAVOR,
    STANDING_THRESHOLDS,
    QuestDifficulty,
    SideQuestOfferStatus,
    Standing,
)

# Line kinds a voice can answer for.
OFFER = "offer"
ACCEPT = "accept"
DECLINE = "decline"
COMPLETE = "complete"
FAIL = "fail"
EXPIRE = "expire"

DEFAULT_BAND = "default"

# What each ending is worth. Clearing a trial is worth more the harder it was;
# abandoning one costs on the same curve, because a constellation minds an
# abandoned S-rank more than an abandoned E.
#
# The asymmetries are deliberate. Declining costs almost nothing — saying no is
# allowed, and a system that resents it would make the opt-in a trap. Ignoring
# costs a little more than declining, because it leaves the thing hanging.
# Withdrawal costs nothing at all: that ending was the constellation's doing.
FAVOR_ON_COMPLETE_BASE = 3
FAVOR_ON_COMPLETE_PER_RANK = 2
FAVOR_ON_FAIL_BASE = -2
FAVOR_ON_FAIL_PER_RANK = -2
FAVOR_ON_DECLINE = -1
FAVOR_ON_EXPIRE = -2


def standing_for(favor: int) -> Standing:
    """Which band a favor score falls into.

    Derived rather than stored, so retuning the thresholds re-reads every
    player's standing instead of needing a migration.
    """
    band = STANDING_THRESHOLDS[0][1]
    for threshold, candidate in STANDING_THRESHOLDS:
        if favor >= threshold:
            band = candidate
    return band


def standing_rank(standing: Standing) -> int:
    """Position on the ladder, 0 for FORSAKEN upward.

    Lets `min_standing` on a broadcast be a comparison rather than a set.
    """
    return list(Standing).index(standing)


def meets_standing(standing: Standing, required: Standing | None) -> bool:
    """Whether a player at `standing` is allowed what `required` asks for."""
    if required is None:
        return True
    return standing_rank(standing) >= standing_rank(required)


def clamp_favor(favor: int) -> int:
    """Hold favor inside its range.

    Bounded so a long history cannot put a player so far out of reach that a
    change of behaviour stops registering — someone who ignored a constellation
    for a year can still climb back with a few cleared trials.
    """
    return max(MIN_FAVOR, min(MAX_FAVOR, favor))


def favor_delta(status: SideQuestOfferStatus, difficulty: QuestDifficulty) -> int:
    """What one ending does to a constellation's regard.

    Only settled endings move favor. An offer still open, or one withdrawn by
    the constellation itself, is worth nothing either way.
    """
    match status:
        case SideQuestOfferStatus.COMPLETED:
            return FAVOR_ON_COMPLETE_BASE + FAVOR_ON_COMPLETE_PER_RANK * difficulty.rank
        case SideQuestOfferStatus.FAILED:
            return FAVOR_ON_FAIL_BASE + FAVOR_ON_FAIL_PER_RANK * difficulty.rank
        case SideQuestOfferStatus.DECLINED:
            return FAVOR_ON_DECLINE
        case SideQuestOfferStatus.EXPIRED:
            return FAVOR_ON_EXPIRE
        case _:
            return 0


def line_kind_for(status: SideQuestOfferStatus) -> str | None:
    """The line kind an ending calls for, if it calls for one."""
    match status:
        case SideQuestOfferStatus.ACCEPTED:
            return ACCEPT
        case SideQuestOfferStatus.DECLINED:
            return DECLINE
        case SideQuestOfferStatus.COMPLETED:
            return COMPLETE
        case SideQuestOfferStatus.FAILED:
            return FAIL
        case SideQuestOfferStatus.EXPIRED:
            return EXPIRE
        case _:
            return None


def _candidates(voice: dict | None, kind: str, standing: Standing) -> list[str]:
    """The lines one voice offers for a kind at a standing, most specific first."""
    if not voice:
        return []
    bands = voice.get(kind) or {}
    if not isinstance(bands, dict):
        return []
    return list(bands.get(standing.value) or bands.get(DEFAULT_BAND) or [])


def pick_line(
    kind: str,
    standing: Standing,
    *,
    overrides: dict | None = None,
    voice: dict | None = None,
    fallback: dict | None = None,
    seed: int = 0,
) -> str | None:
    """What gets said, given everything that might have an opinion about it.

    Resolution runs most specific to least: the broadcast's own line for this
    standing, then its default, then the constellation's, then the plain
    System line. Anything that has nothing to say is skipped rather than
    blanking the message, so a half-written voice degrades to the System's
    register instead of to silence.

    `seed` chooses between alternatives — pass something stable for the thing
    being narrated, such as an offer id, and the same event always reads the
    same way.
    """
    for source in (overrides, voice, fallback):
        options = _candidates(source, kind, standing)
        if options:
            return options[seed % len(options)]
    return None
