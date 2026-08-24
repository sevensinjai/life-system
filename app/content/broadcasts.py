"""The side quests themselves, as written.

Each entry is a trial one constellation issues, with the mechanical shape it
takes (rank, target, reward, penalty, how long you get) and the announcement
it goes out with. The scheduler in `services/broadcasting.py` picks one of
these and puts it on the calendar; nothing here decides *when*.

A few rules the catalog follows, so that the promises the data structure makes
stay true in the content as well:

* **Most trials carry no penalty.** `penalty_exp` stays zero unless the trial
  is one you would only accept knowingly — and even then it stays well under
  the reward. A side quest is an offer, not a debt.
* **Nothing is unbounded.** Every trial states a target and a window a person
  could actually clear in that window.
* **Nothing needs equipment, money, or anywhere to be.** These go out to
  everybody at once; a trial only one kind of life can clear is not a
  broadcast, it is an exclusion.
"""

from dataclasses import dataclass, field
from typing import Any

from app.models.enums import QuestDifficulty, Standing, StatName


@dataclass(frozen=True)
class BroadcastEntry:
    """One side quest as written, before it has a time attached."""

    code: str
    constellation: str  # a Constellation.code
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


BROADCASTS: tuple[BroadcastEntry, ...] = (
    # -- Xingtian 刑天: going on -------------------------------------------
    BroadcastEntry(
        code="xingtian.hundred",
        constellation="xingtian",
        title="One hundred, in one day",
        description=(
            "A hundred of whatever you do to make yourself stronger. Push-ups, "
            "squats, the stairs. Split them across the day if you like — I am "
            "counting the hundred, not the manner of it."
        ),
        difficulty=QuestDifficulty.C,
        target_count=100,
        unit="reps",
        stat_reward=StatName.STRENGTH,
        stat_reward_amount=1,
        window_hours=24,
    ),
    BroadcastEntry(
        code="xingtian.before_dawn",
        constellation="xingtian",
        title="Up before you want to be",
        description=(
            "Once, in the next two days, get up the first time you wake and "
            "do not lie back down. That is the whole trial. It is harder than "
            "the hundred."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="mornings",
        window_hours=48,
    ),
    BroadcastEntry(
        code="xingtian.after_the_fall",
        constellation="xingtian",
        title="The set after the one you failed",
        description=(
            "Find the thing you gave up on this week and do one more of it. "
            "One. Not the whole thing — the one after the one that stopped you."
        ),
        difficulty=QuestDifficulty.B,
        target_count=1,
        unit="attempts",
        penalty_exp=100,
        window_hours=72,
        min_standing=Standing.NOTICED,
    ),
    # -- Hermes 赫爾墨斯: ground covered -------------------------------------
    BroadcastEntry(
        code="hermes.ten_thousand",
        constellation="hermes",
        title="Ten thousand steps",
        description=(
            "Cover ten thousand steps before this closes. They do not have to "
            "be fast and they do not have to be anywhere."
        ),
        difficulty=QuestDifficulty.C,
        target_count=10000,
        unit="steps",
        stat_reward=StatName.AGILITY,
        stat_reward_amount=1,
        window_hours=36,
    ),
    BroadcastEntry(
        code="hermes.three_walks",
        constellation="hermes",
        title="Three walks, any length",
        description=(
            "Three times, go outside and walk with no destination. Ten "
            "minutes counts. The point is the going out, three separate times."
        ),
        difficulty=QuestDifficulty.D,
        target_count=3,
        unit="walks",
        window_hours=72,
    ),
    BroadcastEntry(
        code="hermes.long_way",
        constellation="hermes",
        title="The long way round",
        description=(
            "Once, take the longer route somewhere you were going anyway. "
            "You will be late. That is the trial."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="journeys",
        window_hours=48,
    ),
    # -- Yan Hui 顏回: going without ----------------------------------------
    BroadcastEntry(
        code="yan_hui.one_day",
        constellation="yan_hui",
        title="A day without the one thing",
        description=(
            "You know what it is. You thought of it as you read this line. "
            "One day without it."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="days",
        stat_reward=StatName.VITALITY,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="yan_hui.eight_glasses",
        constellation="yan_hui",
        title="Eight glasses of water",
        description=(
            "Plain water, eight times, before this closes. An unglamorous "
            "trial. Most of them are."
        ),
        difficulty=QuestDifficulty.E,
        target_count=8,
        unit="glasses",
        window_hours=24,
    ),
    BroadcastEntry(
        code="yan_hui.hour_of_quiet",
        constellation="yan_hui",
        title="One hour, nothing in your hands",
        description=(
            "An hour awake with no screen, no book, no music. Sit with the "
            "quiet or walk in it. Do not fill it."
        ),
        difficulty=QuestDifficulty.B,
        target_count=1,
        unit="hours",
        window_hours=72,
        min_standing=Standing.NOTICED,
    ),
    # -- Sugawara no Michizane 菅原道真: study -------------------------------
    BroadcastEntry(
        code="michizane.thirty_pages",
        constellation="michizane",
        title="Thirty pages",
        description="Thirty pages of anything you are not required to read.",
        difficulty=QuestDifficulty.D,
        target_count=30,
        unit="pages",
        stat_reward=StatName.INTELLIGENCE,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="michizane.explain_it",
        constellation="michizane",
        title="Explain it to somebody",
        description=(
            "Take one thing you learned this week and explain it out loud to "
            "another person. If you cannot, you had not learned it."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="explanations",
        window_hours=72,
    ),
    BroadcastEntry(
        code="michizane.finish_it",
        constellation="michizane",
        title="Finish the one you abandoned",
        description=(
            "The book, the course, the half-written thing. Not all of it — "
            "one more session of it, today or tomorrow."
        ),
        difficulty=QuestDifficulty.B,
        target_count=1,
        unit="sessions",
        penalty_exp=100,
        window_hours=48,
        min_standing=Standing.FAVORED,
    ),
    # -- Argus Panoptes 阿爾戈斯: attention ----------------------------------
    BroadcastEntry(
        code="argus.five_things",
        constellation="argus",
        title="Five things you had not noticed",
        description=(
            "Find five things on a route you take every day that you have "
            "never actually looked at. Write them down or do not; I will know."
        ),
        difficulty=QuestDifficulty.D,
        target_count=5,
        unit="things",
        stat_reward=StatName.PERCEPTION,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="argus.ask_once",
        constellation="argus",
        title="Ask somebody how they actually are",
        description=(
            "Once, ask a person you see often and wait through the first "
            "answer for the second one."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="conversations",
        window_hours=72,
    ),
    BroadcastEntry(
        code="argus.ten_minutes",
        constellation="argus",
        title="Ten minutes at the window",
        description=(
            "Ten minutes looking out of a window at whatever is out there. "
            "No phone. This is not meditation; it is just looking."
        ),
        difficulty=QuestDifficulty.E,
        target_count=10,
        unit="minutes",
        window_hours=24,
    ),
    # -- Amaterasu 天照大神: coming back -------------------------------------
    BroadcastEntry(
        code="amaterasu.come_back",
        constellation="amaterasu",
        title="The thing you stopped doing",
        description=(
            "Whatever you were doing daily until you stopped — do it once "
            "more. Badly is fine. Briefly is fine."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="returns",
        window_hours=72,
    ),
    BroadcastEntry(
        code="amaterasu.same_hour",
        constellation="amaterasu",
        title="Two days at the same hour",
        description=(
            "Do one small thing at the same hour on two days running. Any "
            "hour, any thing. It is the sameness I am after."
        ),
        difficulty=QuestDifficulty.D,
        target_count=2,
        unit="days",
        window_hours=72,
    ),
    BroadcastEntry(
        code="amaterasu.lights_out",
        constellation="amaterasu",
        title="Lights out at the hour you chose",
        description=(
            "Pick the hour now. Be in bed at it, once, in the next two nights. "
            "I keep the light so that you need not."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="nights",
        stat_reward=StatName.VITALITY,
        stat_reward_amount=1,
        window_hours=48,
    ),
)


def by_code() -> dict[str, BroadcastEntry]:
    """The catalog keyed by code."""
    return {entry.code: entry for entry in BROADCASTS}


def for_constellation(code: str) -> tuple[BroadcastEntry, ...]:
    """Everything one constellation has to issue."""
    return tuple(entry for entry in BROADCASTS if entry.constellation == code)


def as_lines_payload(entry: BroadcastEntry) -> dict[str, Any]:
    """This trial's line overrides, as they are stored."""
    return {
        kind: {standing: list(lines) for standing, lines in bands.items()}
        for kind, bands in entry.lines.items()
    }
