"""Enumerations shared across the domain."""

from enum import StrEnum


class ScheduleKind(StrEnum):
    """How often a quest comes around.

    Every recurring kind works the same way: it opens a period, you make
    progress inside it, and letting the period end unfinished costs you EXP.
    Only the length and placement of the period differ.
    """

    ONCE = "once"
    DAILY = "daily"
    WEEKDAYS = "weekdays"
    INTERVAL = "interval"
    WEEKLY = "weekly"


class QuestDifficulty(StrEnum):
    """The E-through-S rank ladder. Difficulty sets the default EXP reward."""

    E = "E"
    D = "D"
    C = "C"
    B = "B"
    A = "A"
    S = "S"

    @property
    def rank(self) -> int:
        """Position on the ladder, 0 for E through 5 for S.

        Ranks are declared in ascending order, so comparing them is comparing
        positions. A player who caps their side quests at B rank is saying
        "nothing above index 3".
        """
        return list(QuestDifficulty).index(self)


class QuestStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class SideQuestStatus(StrEnum):
    """Where a side quest broadcast is in its life.

    Unlike a quest instance, a broadcast is one row shared by everyone, so its
    status describes the sky rather than any one player: whether the thing has
    been announced, whether its window is over, whether it was called off.
    """

    DRAFT = "draft"          # written, not going anywhere yet
    SCHEDULED = "scheduled"  # queued to go out at broadcast_at
    BROADCAST = "broadcast"  # announced; offers exist
    CLOSED = "closed"        # window over, answered or not
    CANCELLED = "cancelled"  # called off; every open offer is void


class SideQuestOfferStatus(StrEnum):
    """One player's side of a broadcast.

    DECLINED, EXPIRED and WITHDRAWN all end an offer without a penalty, and
    they are kept apart on purpose: passing on a side quest, never answering
    one, and having it withdrawn are different stories, and only FAILED — a
    quest taken up and then let go — can ever cost EXP.
    """

    OFFERED = "offered"      # reached the player, awaiting an answer
    ACCEPTED = "accepted"    # taken up; progress counts
    DECLINED = "declined"    # passed on, deliberately
    COMPLETED = "completed"
    FAILED = "failed"        # accepted, then the window closed unfinished
    EXPIRED = "expired"      # never answered before the window closed
    WITHDRAWN = "withdrawn"  # the broadcast itself was cancelled


class FriendshipStatus(StrEnum):
    """Where one request to befriend a constellation ended up.

    A constellation is asked, not joined. It may decline to hear you at all,
    and if it does hear you it sets a trial first — so a request has two
    places it can end, and both of them start the same cooling-off period
    before you may ask again.
    """

    CHALLENGED = "challenged"  # it set you a trial; the answer is still open
    ACCEPTED = "accepted"      # you cleared the trial; you are friends
    REFUSED = "refused"        # it would not hear you this time
    FAILED = "failed"          # it heard you, and you did not clear the trial
    WITHDRAWN = "withdrawn"    # the trial was called off; no fault of yours


class Standing(StrEnum):
    """Where a player sits in one constellation's regard.

    Standing is a story value, never a mechanical punishment: it decides how a
    constellation speaks to you and what it is willing to send you, and it can
    never take EXP, levels, or stats. The worst a constellation can do is stop
    finding you interesting.
    """

    FORSAKEN = "forsaken"    # it has written you off
    SLIGHTED = "slighted"    # you have let it down more than once
    STRANGER = "stranger"    # it does not know you yet; where everyone starts
    NOTICED = "noticed"      # it has begun to watch
    FAVORED = "favored"      # it speaks to you directly
    CHAMPION = "champion"    # you are the one it points to


class SideQuestFrequency(StrEnum):
    """How often a player wants the sky to interrupt them.

    Opting in is not a blank cheque: the System broadcasts on its own schedule,
    and this is the player's say over how much of that reaches them.
    """

    RARE = "rare"
    OCCASIONAL = "occasional"
    FREQUENT = "frequent"


class StatName(StrEnum):
    STRENGTH = "strength"
    AGILITY = "agility"
    VITALITY = "vitality"
    INTELLIGENCE = "intelligence"
    PERCEPTION = "perception"


class EventType(StrEnum):
    """Entries in the player's system log — what the app renders as notifications."""

    QUEST_CREATED = "quest_created"
    QUEST_PROGRESS = "quest_progress"
    QUEST_COMPLETED = "quest_completed"
    QUEST_FAILED = "quest_failed"
    LEVEL_UP = "level_up"
    STATS_ALLOCATED = "stats_allocated"
    PENALTY_APPLIED = "penalty_applied"
    DAILY_RESET = "daily_reset"
    SIDE_QUEST_OFFERED = "side_quest_offered"
    SIDE_QUEST_ACCEPTED = "side_quest_accepted"
    SIDE_QUEST_DECLINED = "side_quest_declined"
    SIDE_QUEST_PROGRESS = "side_quest_progress"
    SIDE_QUEST_COMPLETED = "side_quest_completed"
    SIDE_QUEST_FAILED = "side_quest_failed"
    SIDE_QUEST_EXPIRED = "side_quest_expired"
    SIDE_QUEST_WITHDRAWN = "side_quest_withdrawn"
    FRIENDSHIP_REFUSED = "friendship_refused"
    FRIENDSHIP_FORMED = "friendship_formed"
    FRIENDSHIP_FAILED = "friendship_failed"
    FRIENDSHIP_ENDED = "friendship_ended"


# Default EXP awarded for clearing a quest of each difficulty.
DIFFICULTY_EXP: dict[QuestDifficulty, int] = {
    QuestDifficulty.E: 50,
    QuestDifficulty.D: 100,
    QuestDifficulty.C: 200,
    QuestDifficulty.B: 400,
    QuestDifficulty.A: 800,
    QuestDifficulty.S: 1600,
}


# How many side quest offers a week each frequency allows through. The System
# broadcasts as often as it likes; this is what the player actually receives.
SIDE_QUEST_OFFERS_PER_WEEK: dict[SideQuestFrequency, int] = {
    SideQuestFrequency.RARE: 1,
    SideQuestFrequency.OCCASIONAL: 3,
    SideQuestFrequency.FREQUENT: 7,
}


# The favor a standing band begins at, from worst to best. A band runs from
# its own threshold up to the next one, which is what makes `standing_for`
# a lookup rather than a chain of comparisons.
STANDING_THRESHOLDS: tuple[tuple[int, Standing], ...] = (
    (-100, Standing.FORSAKEN),
    (-20, Standing.SLIGHTED),
    (0, Standing.STRANGER),
    (10, Standing.NOTICED),
    (30, Standing.FAVORED),
    (75, Standing.CHAMPION),
)

# Favor is clamped to this range, so a long history cannot put a player so far
# out of reach that a change of behaviour stops registering.
MIN_FAVOR = -100
MAX_FAVOR = 100
