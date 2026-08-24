"""The auditions the Greek constellations set.

One per constellation: the smallest true test of what that figure is
remembered for, set for whoever asks to be befriended.
"""

from app.content.entries import BroadcastEntry
from app.models.enums import QuestDifficulty

GREEK_CHALLENGES: dict[str, BroadcastEntry] = {
    "hermes": BroadcastEntry(
        code="hermes.admission",
        constellation="hermes",
        title="Two thousand steps",
        description=(
            "Travel with me once before you ask to travel with me often. Two "
            "thousand steps. Any two thousand."
        ),
        difficulty=QuestDifficulty.E,
        target_count=2000,
        unit="steps",
        window_hours=48,
        lines={
            "offer": {"default": ["Walk with me once, and we will see."]},
            "complete": {"default": ["Then we travel together. Keep up."]},
            "fail": {"default": ["You did not come. The road is unbothered."]},
        },
    ),
    "argus": BroadcastEntry(
        code="argus.admission",
        constellation="argus",
        title="Three things you had not noticed",
        description=(
            "Before I watch you, show me you can watch. Three things on a "
            "route you know by heart that you have never once looked at."
        ),
        difficulty=QuestDifficulty.E,
        target_count=3,
        unit="things",
        window_hours=48,
        lines={
            "offer": {"default": ["Show me you can look. Three will do."]},
            "complete": {"default": ["You looked. I will keep looking at you."]},
            "fail": {"default": ["Nothing. On a route you walk every day."]},
        },
    ),
    "athena": BroadcastEntry(
        code="athena.admission",
        constellation="athena",
        title="One small thing, made",
        description=(
            "Before you ask me for anything, make something. It may be "
            "terrible. It may take ten minutes. It must not have existed "
            "this morning."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="things",
        window_hours=48,
        lines={
            "offer": {"default": ["Make something first. Then we will talk."]},
            "complete": {"default": ["Made. Come into the workshop."]},
            "fail": {"default": ["Nothing made. There is nothing to discuss."]},
        },
    ),
    "heracles": BroadcastEntry(
        code="heracles.admission",
        constellation="heracles",
        title="One thing off the list",
        description=(
            "Whatever you have been avoiding longest. Do it, or do a piece of "
            "it. I was given twelve; you are being asked for one."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="tasks",
        window_hours=48,
        lines={
            "offer": {"default": ["One off the list. Then ask me again."]},
            "complete": {"default": ["Good. Your labours are mine to watch now."]},
            "fail": {"default": ["Still on the list. So is my opinion of you."]},
        },
    ),
    "sisyphus": BroadcastEntry(
        code="sisyphus.admission",
        constellation="sisyphus",
        title="Once, and then once more",
        description=(
            "Do a hard thing today. Do the same hard thing tomorrow. The "
            "second one is the whole of the audition; the first is only how "
            "you get there."
        ),
        difficulty=QuestDifficulty.D,
        target_count=2,
        unit="days",
        window_hours=48,
        lines={
            "offer": {"default": ["Today, and then again tomorrow. That is all it ever is."]},
            "complete": {"default": ["Twice. You understand the hill. Push alongside me."]},
            "fail": {"default": ["It rolled back. Ask me again; I am always here."]},
        },
    ),
    "asclepius": BroadcastEntry(
        code="asclepius.admission",
        constellation="asclepius",
        title="One early night",
        description=(
            "Go to bed early, once, before you ask me about anything else "
            "that ails you. I say this to everybody and nobody likes it."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="nights",
        window_hours=48,
        lines={
            "offer": {"default": ["Sleep first. Then ask me."]},
            "complete": {"default": ["Rested. Now we may begin properly."]},
            "fail": {"default": ["Still tired, then. It is always the same answer."]},
        },
    ),
    "mnemosyne": BroadcastEntry(
        code="mnemosyne.admission",
        constellation="mnemosyne",
        title="Three things from today",
        description=(
            "Write down three things that happened today, before you ask me "
            "to remember you. I keep what is set down."
        ),
        difficulty=QuestDifficulty.E,
        target_count=3,
        unit="things",
        window_hours=24,
        lines={
            "offer": {"default": ["Three things, written. Then I will know who to remember."]},
            "complete": {"default": ["Kept. You are in the well now."]},
            "fail": {"default": ["Nothing kept. The day is gone, then."]},
        },
    ),
    "atalanta": BroadcastEntry(
        code="atalanta.admission",
        constellation="atalanta",
        title="One hundred paces, quickly",
        description=(
            "A hundred paces faster than you would normally walk them. That "
            "is all. I am not asking you to beat me; nobody does that."
        ),
        difficulty=QuestDifficulty.E,
        target_count=100,
        unit="paces",
        window_hours=24,
        lines={
            "offer": {"default": ["Keep up for a hundred paces. Then we will see."]},
            "complete": {"default": ["Fine. Try to stay level."]},
            "fail": {"default": ["A hundred paces. I did ask for very little."]},
        },
    ),
    "hestia": BroadcastEntry(
        code="hestia.admission",
        constellation="hestia",
        title="One corner",
        description=(
            "Put one small part of where you live back in order. A shelf, a "
            "sink, a table. I keep a fire; you can keep a corner."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="corners",
        window_hours=48,
        lines={
            "offer": {"default": ["One corner. That is the whole of it."]},
            "complete": {"default": ["Kept. There is room at my fire for you."]},
            "fail": {"default": ["It stayed as it was. It usually does."]},
        },
    ),
}
