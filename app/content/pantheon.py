"""The constellations: who is watching, and how each of them talks.

Six of them, drawn from real mythology — two Greek, two Chinese, two Japanese
— rather than invented. Each is a figure who is actually remembered for the
thing it now asks of you: the headless god who kept fighting, the student who
was poor and did not mind, the sun that hid in a cave and came back out.

That is also why the two names in the schema line up so neatly. The **real
name** is the figure: 刑天, Hermes, 天照大神. The **code name** is the title it
speaks under, taken from its own story — 「猛志常在」 from the line Tao
Yuanming wrote about Xingtian, 「一簞一瓢」 from the passage in the Analects
about Yan Hui. The title is what appears when it speaks; the name underneath
is the reminder that it was somebody.

Written with the respect owed to figures people still honour. They ask for
persistence, restraint, study and attention — the things they are actually
remembered for — and they are never made ridiculous.

The voice is a mapping of *line kind* to *standing* to a list of alternatives:

    {"offer": {"default": ["..."], "favored": ["..."]}}

A missing standing falls back to "default", and a missing kind falls back to
the plain System lines at the bottom of this module, so a constellation only
has to write the lines where it actually sounds different from the rest.

Line kinds for a side quest: offer, accept, decline, complete, fail, expire.

Line kinds for a request to be befriended: refuse (it would not hear you this
time), befriend (you cleared its trial), rebuff (you did not), farewell (you
ended it). The trial it sets speaks through its own lines, in
`content/challenges.py`.

Interpolation is deliberately absent — a line is a finished sentence, not a
template. Anything the client needs to say alongside it (counts, deadlines,
EXP) is already structured on the event payload, so a line never has to be
parsed or reassembled to be translated.
"""

from dataclasses import dataclass, field
from typing import Any

from app.models.enums import StatName


@dataclass(frozen=True)
class ConstellationEntry:
    """One constellation as written, before it becomes a row.

    `code` is the identifier the database and the catalogs agree on, not a
    name. The names are the two below it: the **code name** it is called by,
    and the **real name** of the figure behind it. Both are given in English
    and Traditional Chinese.
    """

    code: str
    code_name: str
    code_name_zh_hant: str
    real_name: str
    real_name_zh_hant: str
    epithet: str
    epithet_zh_hant: str
    description: str
    domain: StatName | None = None
    voice: dict[str, dict[str, list[str]]] = field(default_factory=dict)


# The lines any constellation falls back to, and the ones a broadcast with no
# constellation behind it uses outright.
SYSTEM_VOICE: dict[str, dict[str, list[str]]] = {
    "offer": {"default": ["A side quest has been issued."]},
    "accept": {"default": ["Side quest accepted."]},
    "decline": {"default": ["Side quest declined."]},
    "complete": {"default": ["Side quest complete."]},
    "fail": {"default": ["Side quest failed."]},
    "expire": {"default": ["The side quest passed you by."]},
    "refuse": {"default": ["Your request was not heard this time."]},
    "befriend": {"default": ["Your request was granted."]},
    "rebuff": {"default": ["The trial went unfinished. The request is closed."]},
    "farewell": {"default": ["The friendship has ended."]},
}


PANTHEON: tuple[ConstellationEntry, ...] = (
    ConstellationEntry(
        code="xingtian",
        code_name="The Will That Remains",
        code_name_zh_hant="「猛志常在」",
        real_name="Xingtian",
        real_name_zh_hant="刑天",
        epithet="who lost his head and went on fighting",
        epithet_zh_hant="首斷而戰不止者",
        description=(
            "Beheaded for challenging the Yellow Emperor, and buried under a "
            "mountain, he stood up with his nipples for eyes and his navel "
            "for a mouth and kept swinging. Tao Yuanming wrote the line his "
            "title comes from: 刑天舞干戚，猛志固常在 — he brandishes axe and "
            "shield, and the fierce will remains. He has no patience for "
            "anyone who talks about how badly they lost. He watches for the "
            "standing-up part."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {
                "default": ["Something is asked of you. Take it up."],
                "stranger": ["You do not know me. Take it up regardless."],
                "favored": ["You again. Good. Take up the axe."],
                "champion": ["I have given the others your name. Do not shame it."],
            },
            "accept": {"default": ["Then begin."]},
            "decline": {
                "default": ["Noted. The axe keeps."],
                "slighted": ["Of course."],
            },
            "complete": {
                "default": ["That is what going on looks like."],
                "champion": ["Again. And you did not look to me first."],
            },
            "fail": {"default": ["You stopped. I saw where."]},
            "expire": {"default": ["You did not answer. That is an answer."]},
            "refuse": {
                "default": ["Not today. Come back having done something."],
                "slighted": ["No."],
            },
            "befriend": {"default": ["You are of my company now. Do not make me regret it."]},
            "rebuff": {"default": ["You asked, and then you stopped. That is the answer."]},
            "farewell": {"default": ["Go. Keep something in your hands wherever you land."]},
        },
    ),
    ConstellationEntry(
        code="hermes",
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
        code="yan_hui",
        code_name="One Basket, One Gourd",
        code_name_zh_hant="「一簞一瓢」",
        real_name="Yan Hui",
        real_name_zh_hant="顏回",
        epithet="who was poor and did not mind",
        epithet_zh_hant="簞瓢屢空而不改其樂者",
        description=(
            "Confucius' best student, who died young. The Analects keep the "
            "line his title comes from: 一簞食，一瓢飲，在陋巷 — one basket of "
            "rice, one gourd of water, a shabby lane; others could not have "
            "borne the misery, and he did not let it change his joy. He sets "
            "trials of going without, and he never explains them."
        ),
        domain=StatName.VITALITY,
        voice={
            "offer": {
                "default": ["Put something down for a while."],
                "favored": ["You have done this before. It gets no easier. Again."],
            },
            "accept": {"default": ["Good. Now the quiet part."]},
            "decline": {"default": ["The bowl is empty either way."]},
            "complete": {"default": ["You wanted it and did not take it. That is the whole trial."]},
            "fail": {"default": ["You took it. There is no scolding here; only the taking."]},
            "expire": {"default": ["The bowl sat there all week."]},
            "refuse": {"default": ["Not now. Ask again when you want it less."]},
            "befriend": {"default": ["Sit. There is nothing here to eat, and that is the point."]},
            "rebuff": {"default": ["You wanted it more than you wanted this."]},
            "farewell": {"default": ["Go well. The bowl stays empty; it was never only mine."]},
        },
    ),
    ConstellationEntry(
        code="michizane",
        code_name="The Plum That Followed",
        code_name_zh_hant="「飛梅之筆」",
        real_name="Sugawara no Michizane",
        real_name_zh_hant="菅原道真",
        epithet="who was sent away, and whose plum tree came after him",
        epithet_zh_hant="見謫而梅隨之者",
        description=(
            "A scholar and minister slandered out of the capital and exiled "
            "to Dazaifu, where he died. The story says the plum tree he had "
            "said goodbye to uprooted itself and flew to him. Enshrined "
            "afterwards as Tenjin, and petitioned ever since by students the "
            "night before an examination. He speaks in short sentences "
            "because he thinks most sentences are too long."
        ),
        domain=StatName.INTELLIGENCE,
        voice={
            "offer": {
                "default": ["There is something you do not know yet."],
                "champion": ["A shelf has been set aside for you. Fill it."],
            },
            "accept": {"default": ["Begin."]},
            "decline": {"default": ["The book waits. Books are good at that."]},
            "complete": {
                "default": ["Recorded."],
                "favored": ["Recorded, and read twice."],
            },
            "fail": {"default": ["Unfinished. The worst kind of book."]},
            "expire": {"default": ["Unopened."]},
            "refuse": {"default": ["Not now. I am reading."]},
            "befriend": {"default": ["Accepted. Speak quietly."]},
            "rebuff": {"default": ["Withdrawn. Ten pages was not much to ask."]},
            "farewell": {"default": ["Return the book on your way out."]},
        },
    ),
    ConstellationEntry(
        code="argus",
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
        code="amaterasu",
        code_name="The Door Opened Again",
        code_name_zh_hant="「岩戶重開」",
        real_name="Amaterasu",
        real_name_zh_hant="天照大神",
        epithet="who went into the cave, and came back out",
        epithet_zh_hant="入岩戶而復出者",
        description=(
            "The sun, who took offence and shut herself in the rock cave of "
            "heaven, and left the world dark until the other gods laughed "
            "loudly enough outside that she looked out to see why. She is not "
            "interested in whether you kept going. She is interested in "
            "whether you came back, and she counts the times you did."
        ),
        domain=None,
        voice={
            "offer": {
                "default": ["Come back to it once more."],
                "forsaken": ["The door is not barred. It never was."],
                "champion": ["You have come back so often I have stopped counting. Come back."],
            },
            "accept": {"default": ["Then I will wait."]},
            "decline": {"default": ["Rest, then. The light keeps."]},
            "complete": {
                "default": ["You came back. That is the only thing I ever ask."],
                "noticed": ["Twice now. I notice these things."],
            },
            "fail": {"default": ["You did not come back this time. The light is still here."]},
            "expire": {"default": ["I waited. It is no matter. I always do."]},
            "refuse": {"default": ["Come again tomorrow and ask. I will be here."]},
            "befriend": {"default": ["Then the light is yours as well."]},
            "rebuff": {"default": ["You did not return. The door stays open regardless."]},
            "farewell": {"default": ["The light stays. It was never conditional."]},
        },
    ),
)


def by_code() -> dict[str, ConstellationEntry]:
    """The pantheon keyed by code, for seeding and for tests."""
    return {entry.code: entry for entry in PANTHEON}


def as_voice_payload(entry: ConstellationEntry) -> dict[str, Any]:
    """The voice as it is stored — a plain JSON-shaped dict."""
    return {
        kind: {standing: list(lines) for standing, lines in bands.items()}
        for kind, bands in entry.voice.items()
    }
