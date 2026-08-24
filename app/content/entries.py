"""The shapes written content takes, before any of it touches the database.

Two dataclasses, kept apart from the catalogs that use them so the
per-tradition modules can import them without importing each other.
"""

from dataclasses import dataclass, field

from app.models.enums import MythTradition, QuestDifficulty, Standing, StatName


@dataclass(frozen=True)
class ConstellationEntry:
    """One constellation as written, before it becomes a row.

    `code` is the identifier the database and the catalogs agree on, not a
    name. The names are the two below it: the **code name** it is called by —
    a title, usually a line out of its own story — and the **real name** of
    the figure behind it. Both are given in English and Traditional Chinese.
    """

    code: str
    tradition: MythTradition
    code_name: str
    code_name_zh_hant: str
    real_name: str
    real_name_zh_hant: str
    epithet: str
    epithet_zh_hant: str
    description: str
    domain: StatName | None = None
    voice: dict[str, dict[str, list[str]]] = field(default_factory=dict)


@dataclass(frozen=True)
class BroadcastEntry:
    """One side quest as written, before it has a time attached.

    The same shape serves both a broadcast and a trial of admission: a trial
    *is* a side quest, and the only difference is that it is addressed to the
    one player who asked for it rather than sent to everybody.
    """

    code: str
    constellation: str  # a ConstellationEntry.code
    title: str
    description: str
    difficulty: QuestDifficulty = QuestDifficulty.E
    target_count: int = 1
    unit: str | None = None
    exp_reward: int | None = None  # None takes the rank's default
    stat_reward: StatName | None = None
    stat_reward_amount: int = 0
    penalty_exp: int = 0
    # How long players get once it goes out.
    window_hours: int = 48
    min_level: int = 1
    max_level: int | None = None
    min_standing: Standing | None = None
    # Overrides for this trial's own lines, shaped like a constellation voice.
    lines: dict[str, dict[str, list[str]]] = field(default_factory=dict)
