"""The trials the Greek constellations set.

Two or three each: a road, a labour, a stone rolled once more, an hour of
sleep, five things written down, a route run faster, one corner put right.
"""


from app.content.entries import BroadcastEntry
from app.models.enums import QuestDifficulty, StatName

GREEK_TRIALS: tuple[BroadcastEntry, ...] = (
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
    # -- Athena 雅典娜: the craft ------------------------------------------
    BroadcastEntry(
        code="athena.one_thing_made",
        constellation="athena",
        title="One thing, made by hand",
        description=(
            "Make something. Badly is expected. A meal from nothing, a "
            "shelf, a drawing, a repair — the requirement is that it did not "
            "exist this morning and does now."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="things",
        window_hours=72,
    ),
    BroadcastEntry(
        code="athena.learn_the_tool",
        constellation="athena",
        title="Learn the tool you use every day",
        description=(
            "Half an hour on something you have used for years without ever "
            "reading about — the software, the knife, the instrument, the "
            "language. You are almost certainly using it at a quarter of it."
        ),
        difficulty=QuestDifficulty.C,
        target_count=30,
        unit="minutes",
        stat_reward=StatName.INTELLIGENCE,
        stat_reward_amount=1,
        window_hours=72,
    ),
    # -- Heracles 赫拉克勒斯: the list ---------------------------------------
    BroadcastEntry(
        code="heracles.the_list",
        constellation="heracles",
        title="Write the list, then take one off it",
        description=(
            "Every task you have been avoiding, written down in one place. "
            "Then do the smallest one. The list is not the trial; the list is "
            "how you find out how short the trial is."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="tasks",
        stat_reward=StatName.STRENGTH,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="heracles.carry_it",
        constellation="heracles",
        title="Ten minutes carrying something heavy",
        description=(
            "Shopping, water, a bag, a child, your own body up a hill. Ten "
            "minutes under load. None of my labours were more complicated "
            "than this."
        ),
        difficulty=QuestDifficulty.D,
        target_count=10,
        unit="minutes",
        window_hours=48,
    ),
    # -- Sisyphus 薛西弗斯: beginning again ----------------------------------
    BroadcastEntry(
        code="sisyphus.twice_running",
        constellation="sisyphus",
        title="The same thing, two days running",
        description=(
            "Anything, as long as it is the same on both days and neither day "
            "is easy. The second one is the entire trial. The first is just "
            "how you get to it."
        ),
        difficulty=QuestDifficulty.D,
        target_count=2,
        unit="days",
        window_hours=72,
    ),
    BroadcastEntry(
        code="sisyphus.one_more_rep",
        constellation="sisyphus",
        title="One rep of the thing you quit",
        description=(
            "Not the habit back. Not the streak. One repetition of the thing "
            "you stopped doing, today, and then you may stop again."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="attempts",
        window_hours=48,
    ),
    # -- Asclepius 阿斯克勒庇俄斯: mending ------------------------------------
    BroadcastEntry(
        code="asclepius.an_hour_earlier",
        constellation="asclepius",
        title="An hour earlier, once",
        description=(
            "One night, go to bed an hour before you normally would. Not a "
            "new regime. One night. Most of what people bring me would have "
            "been solved by this."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="nights",
        stat_reward=StatName.VITALITY,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="asclepius.the_part_that_hurts",
        constellation="asclepius",
        title="Ten minutes on the part that hurts",
        description=(
            "The shoulder, the back, the knee, the wrist — the one that has "
            "been complaining for months. Ten minutes of stretching it, "
            "resting it, or reading about it properly."
        ),
        difficulty=QuestDifficulty.D,
        target_count=10,
        unit="minutes",
        window_hours=48,
    ),
    # -- Mnemosyne 謨涅摩敘涅: keeping ---------------------------------------
    BroadcastEntry(
        code="mnemosyne.five_things",
        constellation="mnemosyne",
        title="Five things from today, written down",
        description=(
            "Five things that happened today. Not important ones — that is "
            "not the test. In ten years the unimportant ones are the only "
            "part you will want back."
        ),
        difficulty=QuestDifficulty.D,
        target_count=5,
        unit="things",
        window_hours=24,
    ),
    BroadcastEntry(
        code="mnemosyne.by_heart",
        constellation="mnemosyne",
        title="Four lines, by heart",
        description=(
            "A verse, a passage, a set of directions, a phone number. Four "
            "lines held in your own head where no battery is required."
        ),
        difficulty=QuestDifficulty.C,
        target_count=4,
        unit="lines",
        stat_reward=StatName.INTELLIGENCE,
        stat_reward_amount=1,
        window_hours=72,
    ),
    # -- Atalanta 亞特蘭妲: not stopping -------------------------------------
    BroadcastEntry(
        code="atalanta.once_quicker",
        constellation="atalanta",
        title="Once, quicker than usual",
        description=(
            "A route you walk often, done faster than you normally do it. "
            "Once. You do not have to enjoy it."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="journeys",
        window_hours=48,
    ),
    BroadcastEntry(
        code="atalanta.no_apples",
        constellation="atalanta",
        title="Twenty minutes, no apples",
        description=(
            "Twenty minutes of moving with the phone away — pocket, bag, "
            "another room. Somebody rolled gold across my track once and I "
            "have never stopped hearing about it."
        ),
        difficulty=QuestDifficulty.C,
        target_count=20,
        unit="minutes",
        stat_reward=StatName.AGILITY,
        stat_reward_amount=1,
        window_hours=48,
    ),
    # -- Hestia 赫斯提亞: keeping the hearth ---------------------------------
    BroadcastEntry(
        code="hestia.one_corner",
        constellation="hestia",
        title="One corner, put right",
        description=(
            "One small area of where you live, restored to how you would like "
            "it. A drawer. A shelf. The table. Not the whole room; I am not "
            "unreasonable."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="corners",
        window_hours=48,
    ),
    BroadcastEntry(
        code="hestia.one_meal_at_a_table",
        constellation="hestia",
        title="One meal at a table",
        description=(
            "Sitting down, at a table, with nothing playing. One meal. It is "
            "the oldest thing I ask and the one people find hardest."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="meals",
        window_hours=48,
    ),
)
