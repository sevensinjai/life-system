"""The auditions the Chinese constellations set.

One per constellation: the smallest true test of what that figure is
remembered for, set for whoever asks to be befriended.
"""

from app.content.entries import BroadcastEntry
from app.models.enums import QuestDifficulty

CHINESE_CHALLENGES: dict[str, BroadcastEntry] = {
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
    "guan_yu": BroadcastEntry(
        code="guan_yu.admission",
        constellation="guan_yu",
        title="One promise, kept",
        description=(
            "Something you told somebody you would do. Do it before this "
            "closes, or tell them you will not. I will accept either."
        ),
        difficulty=QuestDifficulty.D,
        target_count=1,
        unit="promises",
        window_hours=48,
        lines={
            "offer": {"default": ["Show me your word is worth something. One promise."]},
            "complete": {"default": ["Then we are sworn. I take that seriously."]},
            "fail": {"default": ["You said you would. That is my answer."]},
        },
    ),
    "jingwei": BroadcastEntry(
        code="jingwei.admission",
        constellation="jingwei",
        title="One pebble",
        description=(
            "One minute of work on the thing that is far too large. One. Then "
            "put it down. That is how the sea gets filled."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="minutes",
        window_hours=24,
        lines={
            "offer": {"default": ["One pebble. Bring it here."]},
            "complete": {"default": ["Then fly beside me. Bring something small each day."]},
            "fail": {"default": ["Not one pebble. The sea noticed nothing either way."]},
        },
    ),
    "kuafu": BroadcastEntry(
        code="kuafu.admission",
        constellation="kuafu",
        title="Walk toward something you can see",
        description=(
            "Pick a point on the horizon and go to it on foot. Not far. Just "
            "further than you were going to."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="journeys",
        window_hours=48,
        lines={
            "offer": {"default": ["Chase something small. Then ask me again."]},
            "complete": {"default": ["Then run with me. I warn you how it ends."]},
            "fail": {"default": ["You did not set out. The sun went down anyway."]},
        },
    ),
    "cangjie": BroadcastEntry(
        code="cangjie.admission",
        constellation="cangjie",
        title="Twenty words, by hand",
        description=(
            "Twenty words on paper, in your own writing, about anything at "
            "all. I did not invent this so it could go unused."
        ),
        difficulty=QuestDifficulty.E,
        target_count=20,
        unit="words",
        window_hours=24,
        lines={
            "offer": {"default": ["Twenty words in your own hand. Then we will speak."]},
            "complete": {"default": ["Written. You may use the marks."]},
            "fail": {"default": ["Twenty words. The ghosts wept for less."]},
        },
    ),
    "shennong": BroadcastEntry(
        code="shennong.admission",
        constellation="shennong",
        title="One thing you have never eaten",
        description=(
            "Try one food you have never had. Notice what it does. I was "
            "poisoned seventy times a day for this method; you get a snack."
        ),
        difficulty=QuestDifficulty.E,
        target_count=1,
        unit="tastings",
        window_hours=48,
        lines={
            "offer": {"default": ["Taste one new thing. Then ask."]},
            "complete": {"default": ["Then eat with me. Some of it will be strange."]},
            "fail": {"default": ["Nothing new. You will go on guessing."]},
        },
    ),
    "qianliyan": BroadcastEntry(
        code="qianliyan.admission",
        constellation="qianliyan",
        title="Five sounds",
        description=(
            "Sit still and name five separate sounds you can hear. It takes "
            "longer than you would think."
        ),
        difficulty=QuestDifficulty.E,
        target_count=5,
        unit="sounds",
        window_hours=24,
        lines={
            "offer": {"default": ["Five sounds. Show me you are paying attention."]},
            "complete": {"default": ["Then stand here beside me and look out."]},
            "fail": {"default": ["Not five. And the room was full of them."]},
        },
    ),
    "change": BroadcastEntry(
        code="change.admission",
        constellation="change",
        title="Ten minutes alone",
        description=(
            "Ten minutes with no other person and nothing playing. If that "
            "sounds easy, you have not tried it recently."
        ),
        difficulty=QuestDifficulty.E,
        target_count=10,
        unit="minutes",
        window_hours=24,
        lines={
            "offer": {"default": ["Ten minutes of quiet. Then ask me again."]},
            "complete": {"default": ["Then look up sometimes. I am the one that is always there."]},
            "fail": {"default": ["You filled it with noise. Most people do."]},
        },
    ),
}
