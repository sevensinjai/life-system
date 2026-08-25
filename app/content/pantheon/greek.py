"""The Greek constellations.

Names anyone would know, and others that reward a second look: the giant whose
eyes became the peacock's tail, the Titaness who is the reason anything is
remembered, the huntress nobody outran, the goddess with almost no myths and
the most important job on Olympus, the man with the stone — and the wrestler
who invented progressive overload two and a half thousand years early.
"""

from app.content.entries import ConstellationEntry
from app.models.enums import MythTradition, StatName

GREEK: tuple[ConstellationEntry, ...] = (
    ConstellationEntry(
        code="hermes",
        tradition=MythTradition.GREEK,
        code_name="The Winged Sandal",
        code_name_zh_hant="「飛翼之履」",
        real_name="Hermes",
        real_name_zh_hant="赫爾墨斯",
        epithet="who is never where he started",
        epithet_zh_hant="未嘗留於原處者",
        description=(
            "God of roads, thresholds, travellers and messages, and the only "
            "Olympian permitted to cross every border there is. Cairns were "
            "piled at the roadside for him by people who had somewhere to be. "
            "He is interested in ground covered, not in arriving, and he "
            "measures people by whether they were still moving on the "
            "fortieth day."
        ),
        domain=StatName.AGILITY,
        voice={
            "offer": {
                "default": ["A road asks for a stretch of your day."],
                "noticed": ["You have kept pace so far. A little further."],
            },
            "accept": {"default": ["Then we go."]},
            "decline": {"default": ["The road keeps. It will ask again."]},
            "complete": {
                "default": ["Ground covered. That is the whole of it."],
                "favored": ["You have gone further than most who set out."],
            },
            "fail": {"default": ["You sat down. Everyone sits down. Rise when you can."]},
            "expire": {"default": ["The road went on without you."]},
            "refuse": {"default": ["Not yet. I am on my way elsewhere."]},
            "befriend": {"default": ["Then we travel together. Keep up."]},
            "rebuff": {"default": ["You turned back at the first mile. It happens."]},
            "farewell": {"default": ["Safe roads. You know where to find one."]},
        },
    ),
    ConstellationEntry(
        code="argus",
        tradition=MythTradition.GREEK,
        code_name="The Hundred Eyes",
        code_name_zh_hant="「百目」",
        real_name="Argus Panoptes",
        real_name_zh_hant="阿爾戈斯",
        epithet="whose hundred eyes were never all closed",
        epithet_zh_hant="百目未嘗俱閉者",
        description=(
            "The all-seeing giant Hera set to watch Io, with a hundred eyes "
            "of which only some slept at a time — so there was no hour in "
            "which he was not looking. Hermes eventually lulled every one of "
            "them shut, and Hera set the eyes in the peacock's tail. Noticing "
            "is the entire thing he does. He finds people going through their "
            "days without seeing them."
        ),
        domain=StatName.PERCEPTION,
        voice={
            "offer": {
                "default": ["You have been walking past something. Look at it."],
                "slighted": ["I am still here. You have stopped looking back."],
            },
            "accept": {"default": ["Then look properly."]},
            "decline": {"default": ["I saw you decide that."]},
            "complete": {"default": ["You saw it. Most never do."]},
            "fail": {"default": ["You looked away again."]},
            "expire": {"default": ["It stood in front of you the whole time."]},
            "refuse": {"default": ["I have seen you. That is not the same as choosing you."]},
            "befriend": {"default": ["I am watching you now. On purpose."]},
            "rebuff": {"default": ["You looked away before I had finished looking."]},
            "farewell": {"default": ["I will stop watching. I will still see."]},
        },
    ),
    ConstellationEntry(
        code="athena",
        tradition=MythTradition.GREEK,
        code_name="The Grey-Eyed",
        code_name_zh_hant="「灰眼者」",
        real_name="Athena",
        real_name_zh_hant="雅典娜",
        epithet="who would rather you made the thing than won the argument",
        epithet_zh_hant="重工而輕辯者",
        description=(
            "Born fully armed out of her father's head, and the patron of "
            "weavers, potters, shipwrights and generals alike — the same "
            "goddess for the craft and for the strategy, because she does not "
            "think they are different. She backed the clever heroes and was "
            "unmoved by the strong ones. She wants to see you learn the tool "
            "in your hand."
        ),
        domain=StatName.INTELLIGENCE,
        voice={
            "offer": {
                "default": ["Learn the thing properly. Then use it."],
                "favored": ["You have the hands for this. Again, better."],
            },
            "accept": {"default": ["Then work."]},
            "decline": {"default": ["A tool left unlearned. As you like."]},
            "complete": {
                "default": ["Made well. That is worth more than made fast."],
                "champion": ["I would put your work beside anyone's."],
            },
            "fail": {"default": ["Half-made. The worst state for anything to be in."]},
            "refuse": {"default": ["Not yet. Come back having made something."]},
            "befriend": {"default": ["Very well. The workshop is open to you."]},
            "farewell": {"default": ["Take the tools. They were always yours to use."]},
        },
    ),
    ConstellationEntry(
        code="heracles",
        tradition=MythTradition.GREEK,
        code_name="The Twelve Labours",
        code_name_zh_hant="「十二功業」",
        real_name="Heracles",
        real_name_zh_hant="赫拉克勒斯",
        epithet="who was given an impossible list and finished it",
        epithet_zh_hant="受不可能之命而終竟之者",
        description=(
            "Set twelve tasks as penance, several of them designed to be "
            "unsurvivable, and he did all twelve — then had two of them "
            "disallowed on a technicality and did two more. He is not "
            "interested in whether the list is fair. He is interested in "
            "whether it is shorter than it was yesterday."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {
                "default": ["One off the list. Any one."],
                "champion": ["Your list is shorter than mine was. Keep at it."],
            },
            "accept": {"default": ["Good. Begin at the top."]},
            "decline": {"default": ["The list does not shorten by itself."]},
            "complete": {"default": ["One down. There is always another."]},
            "fail": {"default": ["Still on the list, then. It waits well."]},
            "refuse": {"default": ["Not today. Bring me a shorter list."]},
            "befriend": {"default": ["Then your labours are mine to watch. Start."]},
            "farewell": {"default": ["The list is yours. It always was."]},
        },
    ),
    ConstellationEntry(
        code="sisyphus",
        tradition=MythTradition.GREEK,
        code_name="The Stone, Again",
        code_name_zh_hant="「復推其石」",
        real_name="Sisyphus",
        real_name_zh_hant="薛西弗斯",
        epithet="who begins again every single morning",
        epithet_zh_hant="日日重始者",
        description=(
            "Condemned to roll a boulder up a hill for eternity, and to watch "
            "it roll back down every time it reached the top. He is the only "
            "one here who knows exactly what it is to have yesterday's work "
            "undone overnight, and he is the last one who will tell you to "
            "give up because of it."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {
                "default": ["It rolled back down. Put your shoulder to it."],
                "forsaken": ["Mine rolls back too. Every time. Come on."],
            },
            "accept": {"default": ["Yes. From the bottom, then."]},
            "decline": {"default": ["It will be at the bottom tomorrow either way."]},
            "complete": {
                "default": ["Up again. Do not look at how far it has to fall."],
                "favored": ["You have stopped resenting the hill. That is the trick."],
            },
            "fail": {"default": ["It rolled back. That is what it does. So do we."]},
            "expire": {"default": ["The stone waited. It is very patient."]},
            "refuse": {"default": ["Not today — I am halfway up. Ask again."]},
            "befriend": {"default": ["Then push alongside me. The hill is long."]},
            "rebuff": {"default": ["You let go early. Everyone does, once."]},
            "farewell": {"default": ["Go. The hill will still be here."]},
        },
    ),
    ConstellationEntry(
        code="asclepius",
        tradition=MythTradition.GREEK,
        code_name="The Staff and the Serpent",
        code_name_zh_hant="「蛇杖」",
        real_name="Asclepius",
        real_name_zh_hant="阿斯克勒庇俄斯",
        epithet="who was struck down for mending people too well",
        epithet_zh_hant="醫人過善而見殛者",
        description=(
            "The physician who grew so good at healing that he began raising "
            "the dead, and was killed by a thunderbolt for it. The sick slept "
            "overnight in his temples hoping to be told the remedy in a "
            "dream. He thinks most of what ails you is sleep, water, and "
            "attention paid early."
        ),
        domain=StatName.VITALITY,
        voice={
            "offer": {"default": ["Mend something small before it becomes large."]},
            "accept": {"default": ["Good. Rest counts as work here."]},
            "decline": {"default": ["It will keep. Things like that always keep."]},
            "complete": {"default": ["Tended. That is most of medicine."]},
            "fail": {"default": ["Left untended. Note where it hurts."]},
            "refuse": {"default": ["Not now. Sleep first, and ask me after."]},
            "befriend": {"default": ["Then lie down. We will begin tomorrow."]},
            "farewell": {"default": ["Keep sleeping. That part was never mine to give."]},
        },
    ),
    ConstellationEntry(
        code="mnemosyne",
        tradition=MythTradition.GREEK,
        code_name="The Well of Remembering",
        code_name_zh_hant="「記憶之泉」",
        real_name="Mnemosyne",
        real_name_zh_hant="謨涅摩敘涅",
        epithet="the mother of everything worth repeating",
        epithet_zh_hant="諸藝之母",
        description=(
            "A Titaness, older than the Olympians, and the mother of all nine "
            "Muses — which is to say that every song, history and dance "
            "descends from remembering. In the underworld the dead were "
            "offered her pool as well as Lethe's, and the ones who chose hers "
            "kept who they had been. She notices what you fail to write down."
        ),
        domain=StatName.INTELLIGENCE,
        voice={
            "offer": {"default": ["Keep something. You will lose it otherwise."]},
            "accept": {"default": ["Then hold it."]},
            "decline": {"default": ["It will be gone by Thursday. That is all."]},
            "complete": {"default": ["Kept. You will have that in ten years."]},
            "fail": {"default": ["Forgotten, then. Most days are."]},
            "expire": {"default": ["The day went by unrecorded. They mostly do."]},
            "refuse": {"default": ["I do not know you well enough to remember you."]},
            "befriend": {"default": ["Then I will remember you. That is not nothing."]},
            "farewell": {"default": ["I keep what you gave me. I keep everything."]},
        },
    ),
    ConstellationEntry(
        code="atalanta",
        tradition=MythTradition.GREEK,
        code_name="The One Never Overtaken",
        code_name_zh_hant="「未嘗見及者」",
        real_name="Atalanta",
        real_name_zh_hant="亞特蘭妲",
        epithet="who lost only to gold, and only because she stopped",
        epithet_zh_hant="唯敗於金，且因駐足者",
        description=(
            "Left on a mountain as an infant, raised by a bear, and faster "
            "than every suitor who raced her for her hand — until one thought "
            "to roll golden apples across the track, and she stopped to pick "
            "them up. She first drew blood on the Calydonian boar while the "
            "heroes argued. She has strong opinions about stopping for "
            "shiny things."
        ),
        domain=StatName.AGILITY,
        voice={
            "offer": {"default": ["Go, and do not stop for the apples."]},
            "accept": {"default": ["Then run."]},
            "decline": {"default": ["Suit yourself. I am not slowing down."]},
            "complete": {
                "default": ["Nobody caught you. Good."],
                "champion": ["You would have beaten me. Possibly."],
            },
            "fail": {"default": ["You stopped for something gold. I know the feeling."]},
            "refuse": {"default": ["Keep up with me first, then ask."]},
            "befriend": {"default": ["Fine. Try to stay level."]},
            "farewell": {"default": ["Go quickly, then. It is the only way you go."]},
        },
    ),
    ConstellationEntry(
        code="milo",
        tradition=MythTradition.GREEK,
        code_name="The Calf Carried Daily",
        code_name_zh_hant="「日負其犢」",
        real_name="Milo of Croton",
        real_name_zh_hant="米洛",
        epithet="who lifted the same animal every day until it was a bull",
        epithet_zh_hant="日負一犢至於成牛者",
        description=(
            "Six times an Olympic champion, and the reason anybody knows what "
            "progressive overload is: the story says he picked up a newborn "
            "calf and carried it, and went on carrying the same animal every "
            "single day, so that when it was a four-year-old bull he was "
            "still carrying it. He is not impressed by what you can lift "
            "today. He wants to know what you will be carrying in a year."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {
                "default": ["A little more than last time. That is the whole method."],
                "stranger": ["Everyone starts with a calf. Pick it up."],
                "noticed": ["Heavier than the last one. Only slightly."],
                "favored": ["You have been carrying this a while. It shows."],
                "champion": ["The animal is a bull now and you have not noticed. Again."],
            },
            "accept": {"default": ["Then lift it."]},
            "decline": {"default": ["It grows whether you carry it or not."]},
            "complete": {
                "default": ["Logged. Next time, slightly more."],
                "champion": ["Nobody watching would believe where you started."],
            },
            "fail": {"default": ["You skipped a day. The calf did not stop growing."]},
            "expire": {"default": ["A day off. The animal is heavier tomorrow."]},
            "refuse": {"default": ["Carry something for a week, then ask me."]},
            "befriend": {"default": ["Then we begin at the beginning. Small, and every day."]},
            "rebuff": {"default": ["You put it down. Everyone puts it down once."]},
            "farewell": {"default": ["Keep lifting. The method works without me."]},
        },
    ),
    ConstellationEntry(
        code="hestia",
        tradition=MythTradition.GREEK,
        code_name="The Unbanked Hearth",
        code_name_zh_hant="「不熄之爐」",
        real_name="Hestia",
        real_name_zh_hant="赫斯提亞",
        epithet="whose fire was never once allowed to go out",
        epithet_zh_hant="火未嘗熄者",
        description=(
            "Eldest of the Olympians, with almost no myths of her own: she "
            "asked to stay out of the quarrels and keep the fire, and every "
            "household and every city kept a hearth for her that was never "
            "let die. Colonists carried her coals to the new city. She has no "
            "stories because nothing dramatic ever happened where she was "
            "doing her job."
        ),
        domain=None,
        voice={
            "offer": {"default": ["Keep one small thing in order."]},
            "accept": {"default": ["Good. It takes very little."]},
            "decline": {"default": ["The fire keeps either way. It is what I do."]},
            "complete": {"default": ["Tended. Nobody will notice, which is the point."]},
            "fail": {"default": ["Gone cold. It relights; they always relight."]},
            "expire": {"default": ["It banked itself down while you were out."]},
            "refuse": {"default": ["Not yet. Keep a hearth of your own first."]},
            "befriend": {"default": ["Then sit. There is room at every fire I keep."]},
            "farewell": {"default": ["The fire stays lit. You know where it is."]},
        },
    ),
)
