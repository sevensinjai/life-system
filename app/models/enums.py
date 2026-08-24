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


class QuestStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


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
    SKILL_CREATED = "skill_created"
    SKILL_LEVEL_UP = "skill_level_up"
    STATS_ALLOCATED = "stats_allocated"
    PENALTY_APPLIED = "penalty_applied"
    DAILY_RESET = "daily_reset"


# Default EXP awarded for clearing a quest of each difficulty.
DIFFICULTY_EXP: dict[QuestDifficulty, int] = {
    QuestDifficulty.E: 50,
    QuestDifficulty.D: 100,
    QuestDifficulty.C: 200,
    QuestDifficulty.B: 400,
    QuestDifficulty.A: 800,
    QuestDifficulty.S: 1600,
}
