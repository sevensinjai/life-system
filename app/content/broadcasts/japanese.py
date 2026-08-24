"""The trials the Japanese constellations set.

A thing come back to, ten pages, one head off the serpent, a song sung
through, five minutes where an hour was demanded, three minutes of dancing.
"""


from app.content.entries import BroadcastEntry
from app.models.enums import QuestDifficulty, Standing, StatName

JAPANESE_TRIALS: tuple[BroadcastEntry, ...] = (
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
    # -- Susanoo 須佐之男: one head at a time ---------------------------------
    BroadcastEntry(
        code="susanoo.one_head",
        constellation="susanoo",
        title="One of the eight heads",
        description=(
            "Take the thing that is too big and cut it into eight. Then do "
            "one eighth of it. I did not fight the serpent; I fought a neck, "
            "eight times."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="heads",
        stat_reward=StatName.STRENGTH,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="susanoo.fifteen_minutes_of_storm",
        constellation="susanoo",
        title="Fifteen minutes of storm",
        description=(
            "Next time you are angry, put it somewhere: fifteen minutes of "
            "hard physical effort. I wrecked my sister's hall with mine. "
            "Learn from that."
        ),
        difficulty=QuestDifficulty.D,
        target_count=15,
        unit="minutes",
        window_hours=48,
    ),
    # -- Benzaiten 辯才天: making a sound ------------------------------------
    BroadcastEntry(
        code="benzaiten.one_song",
        constellation="benzaiten",
        title="One song, all the way through",
        description=(
            "Sing it, hum it, play it, badly. All the way to the end without "
            "stopping to be embarrassed. Alone counts, but not by much."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="songs",
        window_hours=48,
    ),
    BroadcastEntry(
        code="benzaiten.the_sentence",
        constellation="benzaiten",
        title="The sentence you have been avoiding",
        description=(
            "There is one you have rehearsed and not said. Say it to the "
            "person it is for. Words are water: held too long they go "
            "stagnant."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="sentences",
        stat_reward=StatName.INTELLIGENCE,
        stat_reward_amount=1,
        window_hours=72,
    ),
    # -- Sukunabikona 少彥名神: the small dose --------------------------------
    BroadcastEntry(
        code="sukunabikona.five_minutes",
        constellation="sukunabikona",
        title="Five minutes is enough",
        description=(
            "The thing you keep not starting because it deserves an hour. "
            "Give it five minutes. I am the size of a thumb and I helped "
            "build a country."
        ),
        difficulty=QuestDifficulty.E,
        target_count=5,
        unit="minutes",
        stat_reward=StatName.VITALITY,
        stat_reward_amount=1,
        window_hours=24,
    ),
    BroadcastEntry(
        code="sukunabikona.one_remedy",
        constellation="sukunabikona",
        title="One small remedy",
        description=(
            "One small thing done for the body: a glass of water, a window "
            "opened, a stretch, a plaster on the cut you have been ignoring. "
            "Small and now beats large and later."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="remedies",
        window_hours=48,
    ),
    # -- Sarutahiko 猿田彥: the fork -----------------------------------------
    BroadcastEntry(
        code="sarutahiko.the_turn",
        constellation="sarutahiko",
        title="The turning you never take",
        description=(
            "On a route you know by heart, take the other way once. You will "
            "arrive late and know one more thing about where you live."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="turnings",
        stat_reward=StatName.AGILITY,
        stat_reward_amount=1,
        window_hours=48,
    ),
    BroadcastEntry(
        code="sarutahiko.show_the_way",
        constellation="sarutahiko",
        title="Show somebody the way",
        description=(
            "Give somebody directions, walk them to the place, or explain the "
            "thing you know that they do not. Standing at the fork is only "
            "useful if you point."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="times",
        window_hours=72,
    ),
    # -- Yatagarasu 八咫烏: going in front -----------------------------------
    BroadcastEntry(
        code="yatagarasu.three_living_things",
        constellation="yatagarasu",
        title="Three living things that are not people",
        description=(
            "A bird, a weed through the pavement, a spider in the corner, a "
            "tree you pass daily. Three of them, properly looked at. You "
            "share the place with more than you have noticed."
        ),
        difficulty=QuestDifficulty.E,
        target_count=3,
        unit="things",
        stat_reward=StatName.PERCEPTION,
        stat_reward_amount=1,
        window_hours=24,
    ),
    BroadcastEntry(
        code="yatagarasu.go_first",
        constellation="yatagarasu",
        title="Go first, once",
        description=(
            "Make the plan, send the message, pick the place, start the "
            "conversation. Somebody has to walk in front and it is usually "
            "the same person."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="times",
        window_hours=72,
    ),
    # -- Ame-no-Uzume 天鈿女命: being ridiculous ------------------------------
    BroadcastEntry(
        code="uzume.three_minutes_dancing",
        constellation="uzume",
        title="Three minutes of dancing badly",
        description=(
            "Where nobody can see, if you must. Three minutes. I did this on "
            "an upturned tub in front of eight hundred gods and it ended a "
            "world-wide darkness, so let us have no talk of dignity."
        ),
        difficulty=QuestDifficulty.E,
        target_count=3,
        unit="minutes",
        window_hours=24,
    ),
    BroadcastEntry(
        code="uzume.one_laugh",
        constellation="uzume",
        title="Somebody else's laugh",
        description=(
            "Make one other person laugh, on purpose. Not a good joke. A "
            "laugh. The gods I got were not laughing at anything clever."
        ),
        difficulty=QuestDifficulty.C,
        target_count=1,
        unit="laughs",
        window_hours=72,
    ),
)
