"""The shapes written content takes, before any of it touches the database.

Two dataclasses and one constructor, kept apart from the catalogs that use
them so the per-tradition modules can import them without importing each
other.

The constructor is `trial`, and it exists because every constellation's
catalogue is a **ladder**. Rank is not decoration: it says how much of a life
the trial asks for, and from that follows how long you get and whether you
have to have earned it. E is minutes and open to strangers; S is a fortnight
and only ever offered to a champion. Encoding that here means a rung is one
line of writing rather than ten lines of bookkeeping, and it means no rung can
quietly be authored with a fortnight's work and a day to do it in.
"""

from dataclasses import dataclass, field

from app.models.enums import MythTradition, QuestDifficulty, Standing, StatName

# How long each rank gives you, and what standing it is kept for. A trial may
# override either, but the ladder is the default and most rungs take it.
RANK_WINDOW_HOURS: dict[QuestDifficulty, int] = {
    QuestDifficulty.E: 24,
    QuestDifficulty.D: 48,
    QuestDifficulty.C: 72,
    QuestDifficulty.B: 96,
    QuestDifficulty.A: 168,
    QuestDifficulty.S: 336,
}

# Nothing below B is gated: a stranger has to be able to start somewhere.
RANK_STANDING: dict[QuestDifficulty, Standing | None] = {
    QuestDifficulty.E: None,
    QuestDifficulty.D: None,
    QuestDifficulty.C: None,
    QuestDifficulty.B: Standing.NOTICED,
    QuestDifficulty.A: Standing.FAVORED,
    QuestDifficulty.S: Standing.CHAMPION,
}


class _Auto:
    """Sentinel: take the ladder's default for this rank."""


AUTO = _Auto()


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


def trial(
    constellation: str,
    slug: str,
    title: str,
    description: str,
    difficulty: QuestDifficulty,
    target_count: int = 1,
    unit: str | None = None,
    *,
    stat: StatName | None = None,
    stat_amount: int = 1,
    penalty_exp: int = 0,
    exp_reward: int | None = None,
    window_hours: int | _Auto = AUTO,
    min_standing: Standing | None | _Auto = AUTO,
    min_level: int = 1,
    max_level: int | None = None,
    lines: dict[str, dict[str, list[str]]] | None = None,
) -> BroadcastEntry:
    """One rung of a constellation's ladder.

    `window_hours` and `min_standing` default to the rank's place on the
    ladder; pass either explicitly where a particular trial needs its own
    terms — a hard thing that still has to happen today, or a B-rank a
    constellation is willing to put in front of anyone.
    """
    return BroadcastEntry(
        code=f"{constellation}.{slug}",
        constellation=constellation,
        title=title,
        description=description,
        difficulty=difficulty,
        target_count=target_count,
        unit=unit,
        exp_reward=exp_reward,
        stat_reward=stat,
        stat_reward_amount=stat_amount if stat else 0,
        penalty_exp=penalty_exp,
        window_hours=(
            RANK_WINDOW_HOURS[difficulty]
            if isinstance(window_hours, _Auto)
            else window_hours
        ),
        min_level=min_level,
        max_level=max_level,
        min_standing=(
            RANK_STANDING[difficulty]
            if isinstance(min_standing, _Auto)
            else min_standing
        ),
        lines=lines or {},
    )
