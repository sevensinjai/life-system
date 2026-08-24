"""The trials of admission: what a constellation sets before it calls you a friend.

A constellation issues to its friends and to nobody else, so this is the way
in. You ask; if it agrees to hear you it sets one of these; clearing it makes
you friends. Failing it, declining it, or letting it lapse ends the request
and starts the wait before you may ask again.

One per constellation, and each is the smallest true test of what that figure
is remembered for — a first meeting, not a proving ground. They are
deliberately easier than the trials that follow, and none of them carries a
penalty: a stranger who fails an audition has lost the audition, which is
punishment enough.
"""

from app.content.broadcasts import BroadcastEntry
from app.models.enums import QuestDifficulty

# Keyed by constellation code. Reuses the broadcast shape, because a challenge
# *is* a side quest — the only difference is that it is addressed to one
# player rather than broadcast to all of them.
CHALLENGES: dict[str, BroadcastEntry] = {
    "xingtian": BroadcastEntry(
        code="xingtian.admission",
        constellation="xingtian",
        title="Twenty, now",
        description=(
            "You want my attention. Twenty of something hard, before this "
            "closes. I am not interested in which twenty."
        ),
        difficulty=QuestDifficulty.D,
        target_count=20,
        unit="reps",
        window_hours=48,
        lines={
            "offer": {"default": ["You asked. Twenty, then. Now."]},
            "complete": {"default": ["Fine. You are of my company."]},
            "fail": {"default": ["Twenty. You asked me for this."]},
            "expire": {"default": ["You asked, and then you did nothing."]},
        },
    ),
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
    "yan_hui": BroadcastEntry(
        code="yan_hui.admission",
        constellation="yan_hui",
        title="One evening, nothing after dark",
        description=(
            "One evening: eat nothing after the light goes. If that is not "
            "your difficulty, choose the thing that is and leave it alone "
            "until morning."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="evenings",
        window_hours=48,
        lines={
            "offer": {"default": ["One evening. Then ask me again."]},
            "complete": {"default": ["You can want a thing and not take it. Sit down."]},
            "fail": {"default": ["You took it. I am not angry; I am only right."]},
        },
    ),
    "michizane": BroadcastEntry(
        code="michizane.admission",
        constellation="michizane",
        title="Ten pages",
        description="Ten pages. Any book. I will know if they were the same page.",
        difficulty=QuestDifficulty.E,
        target_count=10,
        unit="pages",
        window_hours=48,
        lines={
            "offer": {"default": ["Ten pages. Then we will speak."]},
            "complete": {"default": ["Accepted. Your shelf is that one."]},
            "fail": {"default": ["Unread. A short book, too."]},
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
    "amaterasu": BroadcastEntry(
        code="amaterasu.admission",
        constellation="amaterasu",
        title="Come back tomorrow",
        description=(
            "Do one small thing today, and the same small thing tomorrow. "
            "That is all I have ever asked of anyone."
        ),
        difficulty=QuestDifficulty.D,
        target_count=2,
        unit="days",
        window_hours=48,
        lines={
            "offer": {"default": ["Today, and then tomorrow. That is the whole test."]},
            "complete": {"default": ["You came back. Of course you are welcome."]},
            "fail": {"default": ["Only the once. The light stays regardless."]},
            "expire": {"default": ["I waited for you. It is no matter. Ask again."]},
        },
    ),
}


def challenge_for(code: str) -> BroadcastEntry | None:
    """The trial this constellation sets, if it has written one."""
    return CHALLENGES.get(code)
