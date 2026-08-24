"""The auditions the Japanese constellations set.

One per constellation: the smallest true test of what that figure is
remembered for, set for whoever asks to be befriended.
"""

from app.content.entries import BroadcastEntry
from app.models.enums import QuestDifficulty

JAPANESE_CHALLENGES: dict[str, BroadcastEntry] = {
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
    "susanoo": BroadcastEntry(
        code="susanoo.admission",
        constellation="susanoo",
        title="One of the eight",
        description=(
            "Cut the thing that is too big into eight pieces and do one of "
            "them. That is not a metaphor; write down eight and do one."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="heads",
        window_hours=48,
        lines={
            "offer": {"default": ["One head. Then we will see about the rest."]},
            "complete": {"default": ["Then stand with me. I am good in a fight and poor company."]},
            "fail": {"default": ["Still eight. It grows them back if you leave it."]},
        },
    ),
    "benzaiten": BroadcastEntry(
        code="benzaiten.admission",
        constellation="benzaiten",
        title="One song, through",
        description=(
            "Sing or play or hum something from beginning to end without "
            "stopping to be embarrassed halfway."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="songs",
        window_hours=48,
        lines={
            "offer": {"default": ["Let me hear something. Anything will do."]},
            "complete": {"default": ["Then we are in the same water. Make some noise."]},
            "fail": {"default": ["Silence. I can work with very little, but not that."]},
        },
    ),
    "sukunabikona": BroadcastEntry(
        code="sukunabikona.admission",
        constellation="sukunabikona",
        title="Five minutes",
        description=(
            "Five minutes of the thing you have been putting off because it "
            "deserves an hour. Five. Then stop."
        ),
        difficulty=QuestDifficulty.E,
        target_count=5,
        unit="minutes",
        window_hours=24,
        lines={
            "offer": {"default": ["Five minutes. I am small; I ask small things."]},
            "complete": {"default": ["Then I will ask you for very little, very often."]},
            "fail": {"default": ["Not even five. That is a short five minutes."]},
        },
    ),
    "sarutahiko": BroadcastEntry(
        code="sarutahiko.admission",
        constellation="sarutahiko",
        title="One unfamiliar turning",
        description=(
            "Once, on a route you know, go the other way. You will be late "
            "and you will have learned something."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="turnings",
        window_hours=48,
        lines={
            "offer": {"default": ["Take one turning you do not know. Then ask."]},
            "complete": {"default": ["Then ask me at every fork. That is what I am for."]},
            "fail": {"default": ["The usual way. I was standing right there."]},
        },
    ),
    "yatagarasu": BroadcastEntry(
        code="yatagarasu.admission",
        constellation="yatagarasu",
        title="Two living things",
        description=(
            "Two living things that are not people, properly looked at. They "
            "are outside the window. Some of them are inside."
        ),
        difficulty=QuestDifficulty.E,
        target_count=2,
        unit="things",
        window_hours=24,
        lines={
            "offer": {"default": ["Notice two. I will know if you guessed."]},
            "complete": {"default": ["Then I will fly ahead. Look up now and then."]},
            "fail": {"default": ["Not two. And they were all around you."]},
        },
    ),
    "uzume": BroadcastEntry(
        code="uzume.admission",
        constellation="uzume",
        title="Three minutes of moving foolishly",
        description=(
            "Dance, badly, for three minutes, where nobody can see if you "
            "insist. This is the entire audition and I am not embarrassed by "
            "it, so you should not be either."
        ),
        difficulty=QuestDifficulty.E,
        target_count=3,
        unit="minutes",
        window_hours=24,
        lines={
            "offer": {"default": ["Three minutes. Look ridiculous. It works; ask the sun."]},
            "complete": {"default": ["Then dance badly with me. It is the whole of my method."]},
            "fail": {"default": ["You thought about how it would look. Everyone does."]},
        },
    ),
}
