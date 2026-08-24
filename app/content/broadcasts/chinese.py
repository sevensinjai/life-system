"""The trials the Chinese constellations set.

A hundred repetitions, a day without the one thing, a promise kept, a pebble
carried, a horizon looked at, an hour spent alone on purpose.
"""


from app.content.entries import BroadcastEntry
from app.models.enums import QuestDifficulty, Standing, StatName

CHINESE_TRIALS: tuple[BroadcastEntry, ...] = (
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
    # -- Guan Yu 關羽: keeping your word -------------------------------------
    BroadcastEntry(
        code="guan_yu.the_promise",
        constellation="guan_yu",
        title="The promise you let slide",
        description=(
            "You made it to somebody and you have not kept it. Keep it, or "
            "tell them plainly that you will not. Either is honourable. What "
            "you are doing now is not."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="promises",
        stat_reward=StatName.STRENGTH,
        stat_reward_amount=1,
        window_hours=72,
    ),
    BroadcastEntry(
        code="guan_yu.out_of_your_way",
        constellation="guan_yu",
        title="Out of your way, once",
        description=(
            "Do one thing for somebody that costs you real time and gets you "
            "nothing. I rode a thousand li through five passes for this. You "
            "may take a bus."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="favours",
        window_hours=72,
    ),
    # -- Jingwei 精衛: one pebble at a time ----------------------------------
    BroadcastEntry(
        code="jingwei.one_minute",
        constellation="jingwei",
        title="One minute of the impossible thing",
        description=(
            "The project too big to start. Set a timer for one minute and "
            "work on it. Then stop, even if you want to go on. One minute is "
            "a pebble; the sea does not know the difference."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="minutes",
        window_hours=24,
    ),
    BroadcastEntry(
        code="jingwei.three_stones",
        constellation="jingwei",
        title="Three days, one stone each",
        description=(
            "The same impossible thing, touched on three separate days. Five "
            "minutes each is plenty. I have been at this for three thousand "
            "years and the method has not changed."
        ),
        difficulty=QuestDifficulty.C,
        target_count=3,
        unit="days",
        window_hours=72,
    ),
    # -- Kuafu 夸父: closing the distance ------------------------------------
    BroadcastEntry(
        code="kuafu.reach_it",
        constellation="kuafu",
        title="Reach the thing you can see",
        description=(
            "Pick something visible from where you are standing — a tower, a "
            "hill, the end of the street — and go to it on foot. Then come "
            "back, or do not."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="journeys",
        stat_reward=StatName.AGILITY,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="kuafu.before_the_sun",
        constellation="kuafu",
        title="Move before the sun does",
        description=(
            "Once, be outside and moving before sunrise. I raced the thing "
            "and lost; you only have to start before it."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="mornings",
        window_hours=48,
    ),
    # -- Cangjie 倉頡: setting it down ---------------------------------------
    BroadcastEntry(
        code="cangjie.hundred_words",
        constellation="cangjie",
        title="One hundred words, by hand",
        description=(
            "On paper, in your own handwriting. About anything. The hand "
            "remembers differently from the keyboard; that is not "
            "sentimentality, it is why I bothered."
        ),
        difficulty=QuestDifficulty.C,
        target_count=100,
        unit="words",
        stat_reward=StatName.INTELLIGENCE,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="cangjie.proper_name",
        constellation="cangjie",
        title="The proper name for it",
        description=(
            "Something you have been calling 'the thing' — a bird, a part, a "
            "feeling, a tool. Find out what it is actually called. A name is "
            "a handle; without one you cannot pick the thing up."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="names",
        window_hours=48,
    ),
    # -- Shennong 神農: tasting ----------------------------------------------
    BroadcastEntry(
        code="shennong.never_eaten",
        constellation="shennong",
        title="Something you have never eaten",
        description=(
            "One food you have genuinely never tried. Note what it does to "
            "you. This is how the entire pharmacopoeia was written, though I "
            "had a rougher time of it."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="tastings",
        window_hours=72,
    ),
    BroadcastEntry(
        code="shennong.three_plants",
        constellation="shennong",
        title="Three different plants, one day",
        description=(
            "Three distinct plants eaten in a single day. Herbs count. This "
            "is a low bar that most days do not clear."
        ),
        difficulty=QuestDifficulty.C,
        target_count=3,
        unit="plants",
        stat_reward=StatName.VITALITY,
        stat_reward_amount=1,
        window_hours=24,
    ),
    # -- Qianliyan 千里眼: looking further ------------------------------------
    BroadcastEntry(
        code="qianliyan.ten_sounds",
        constellation="qianliyan",
        title="Ten sounds, named",
        description=(
            "Sit still and name ten separate sounds you can hear. My partner "
            "does the hearing; I am told it takes longer than people expect."
        ),
        difficulty=QuestDifficulty.D,
        target_count=10,
        unit="sounds",
        stat_reward=StatName.PERCEPTION,
        stat_reward_amount=1,
        window_hours=24,
    ),
    BroadcastEntry(
        code="qianliyan.horizon",
        constellation="qianliyan",
        title="Two minutes at the furthest thing",
        description=(
            "Find the most distant thing you can see from where you are and "
            "look at it for two minutes. Your eyes have been at arm's length "
            "all week."
        ),
        difficulty=QuestDifficulty.E,
        target_count=2,
        unit="minutes",
        window_hours=24,
    ),
    # -- Chang'e 嫦娥: being alone -------------------------------------------
    BroadcastEntry(
        code="change.an_hour_alone",
        constellation="change",
        title="An hour by yourself",
        description=(
            "One hour with no other person and nothing playing. Alone is not "
            "the same as unaccompanied, and most people have not tried the "
            "first one in years."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="hours",
        window_hours=72,
    ),
    BroadcastEntry(
        code="change.five_minutes_of_sky",
        constellation="change",
        title="Five minutes of sky",
        description=(
            "Go outside and look up for five minutes. If I am there, you will "
            "see me. If I am not, look anyway."
        ),
        difficulty=QuestDifficulty.E,
        target_count=5,
        unit="minutes",
        window_hours=24,
    ),
)
