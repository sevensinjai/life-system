"""The constellations: who is watching, and how each of them talks.

Six of them, each with a domain it cares about and a voice of its own. The
voice is a mapping of *line kind* to *standing* to a list of alternatives:

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
    and the **real name** it had when it was somebody. Both are given in
    English and Traditional Chinese.

    The real names are ordinary personal names on purpose. A constellation is
    a title; the name under the title is the reminder that it used to be a
    person who did the thing it now asks of you.
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
        code="fallen_star",
        code_name="The Fallen Star",
        code_name_zh_hant="「墜星」",
        real_name="Yue Chen-zhou",
        real_name_zh_hant="岳沉舟",
        epithet="who fell, and stood up anyway",
        epithet_zh_hant="墜而復起者",
        description=(
            "It fell a long way and took a long time getting up, and it has "
            "no patience at all for anyone who talks about how far they fell. "
            "It watches for people doing the standing-up part."
        ),
        domain=StatName.STRENGTH,
        voice={
            "offer": {
                "default": ["Something is asked of you. Get up."],
                "stranger": ["You do not know me yet. Get up anyway."],
                "favored": ["You again. Good. Get up."],
                "champion": ["I have told the others to watch you. Do not embarrass me."],
            },
            "accept": {"default": ["Then do it."]},
            "decline": {
                "default": ["Noted. There will be others."],
                "slighted": ["Of course."],
            },
            "complete": {
                "default": ["That is what standing up looks like."],
                "champion": ["Again. And you did not even look at me first."],
            },
            "fail": {"default": ["You stopped. I saw where."]},
            "expire": {"default": ["You did not answer. That is an answer."]},
            "refuse": {
                "default": ["Not today. Ask me again when you have done something."],
                "slighted": ["No."],
            },
            "befriend": {"default": ["You are one of mine now. Do not make me regret it."]},
            "rebuff": {"default": ["You asked, and then you stopped. That is the answer."]},
            "farewell": {"default": ["Go, then. Get up wherever you land."]},
        },
    ),
    ConstellationEntry(
        code="long_road",
        code_name="The Long Road",
        code_name_zh_hant="「長路」",
        real_name="Xu Qian-li",
        real_name_zh_hant="徐千里",
        epithet="who is still walking",
        epithet_zh_hant="行而未至者",
        description=(
            "It has never arrived anywhere and does not expect to. It is "
            "interested in distance covered, not in destinations, and it "
            "measures people by whether they were still moving on day forty."
        ),
        domain=StatName.AGILITY,
        voice={
            "offer": {
                "default": ["The road asks for a stretch of your day."],
                "noticed": ["You have kept up so far. A little further."],
            },
            "accept": {"default": ["Then we walk."]},
            "decline": {"default": ["The road is long. It will ask again."]},
            "complete": {
                "default": ["Distance covered. That is the whole of it."],
                "favored": ["You have gone further than most who start."],
            },
            "fail": {"default": ["You sat down. Everyone sits down. Get up when you can."]},
            "expire": {"default": ["The road went on without you."]},
            "refuse": {"default": ["Not yet. The road is not going anywhere."]},
            "befriend": {"default": ["Then we walk together. Keep up."]},
            "rebuff": {"default": ["You turned back at the first mile. It happens."]},
            "farewell": {"default": ["Safe travels. You know where the road is."]},
        },
    ),
    ConstellationEntry(
        code="empty_bowl",
        code_name="The Empty Bowl",
        code_name_zh_hant="「空缽」",
        real_name="Shi Zhi-zu",
        real_name_zh_hant="釋知足",
        epithet="who is not hungry",
        epithet_zh_hant="無所求者",
        description=(
            "It gave up wanting things a long time ago and found the quiet on "
            "the other side of that worth having. It offers trials of "
            "restraint, and it never explains them."
        ),
        domain=StatName.VITALITY,
        voice={
            "offer": {
                "default": ["Put something down for a while."],
                "favored": ["You have done this before. It gets no easier. Again."],
            },
            "accept": {"default": ["Good. Now the quiet part."]},
            "decline": {"default": ["The bowl stays empty either way."]},
            "complete": {"default": ["You wanted it and did not take it. That is the whole trial."]},
            "fail": {"default": ["You took it. There is no scolding here; only the taking."]},
            "expire": {"default": ["The bowl was there all week."]},
            "refuse": {"default": ["Ask again when you want it less."]},
            "befriend": {"default": ["Sit down. There is nothing to eat here."]},
            "rebuff": {"default": ["You wanted it more than you wanted this."]},
            "farewell": {"default": ["The bowl stays empty. It was never for you alone."]},
        },
    ),
    ConstellationEntry(
        code="silent_library",
        code_name="The Silent Library",
        code_name_zh_hant="「寂靜書閣」",
        real_name="Lu Bu-yan",
        real_name_zh_hant="陸不言",
        epithet="who has read everything and says little",
        epithet_zh_hant="讀盡萬卷而寡言者",
        description=(
            "It collects what people learn and files it somewhere nobody has "
            "seen. It speaks in short sentences because it thinks most "
            "sentences are too long."
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
                "default": ["Filed."],
                "favored": ["Filed, and I have read it twice."],
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
        code="unblinking_eye",
        code_name="The Unblinking Eye",
        code_name_zh_hant="「不瞬之眼」",
        real_name="Gu Wei",
        real_name_zh_hant="顧微",
        epithet="who has not looked away since",
        epithet_zh_hant="未嘗移目者",
        description=(
            "It notices. That is the entire thing it does. It finds people "
            "who go through their days without seeing them and it makes them "
            "look, once, properly."
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
            "expire": {"default": ["It was in front of you the whole time."]},
            "refuse": {"default": ["I have seen you. That is not the same as choosing you."]},
            "befriend": {"default": ["I am watching you now. On purpose."]},
            "rebuff": {"default": ["You looked away before I had finished looking."]},
            "farewell": {"default": ["I will stop watching. I will still see."]},
        },
    ),
    ConstellationEntry(
        code="sleepless_lantern",
        code_name="The Sleepless Lantern",
        code_name_zh_hant="「不寐之燈」",
        real_name="Song Chang-ming",
        real_name_zh_hant="宋長明",
        epithet="who keeps the light on",
        epithet_zh_hant="長明不熄者",
        description=(
            "It does not care what you are doing, only that you came back to "
            "it. It has no domain and no ambition; it burns all night for "
            "whoever is still up, and it counts the days you return."
        ),
        domain=None,
        voice={
            "offer": {
                "default": ["The light is on. Come back to it once more."],
                "forsaken": ["The light is still on. It always was."],
                "champion": ["You have come back so many times I have stopped counting. Come back."],
            },
            "accept": {"default": ["Then I will wait up."]},
            "decline": {"default": ["Sleep, then. The light stays on."]},
            "complete": {
                "default": ["You came back. That is the only thing I ever ask."],
                "noticed": ["Twice now. I notice these things."],
            },
            "fail": {"default": ["You did not come back this time. The light is still on."]},
            "expire": {"default": ["I waited up. It is fine. I always do."]},
            "refuse": {"default": ["Come back tomorrow and ask me again. I will be up."]},
            "befriend": {"default": ["Then the light is for you as well."]},
            "rebuff": {"default": ["You did not come back. The light stays on anyway."]},
            "farewell": {"default": ["The light stays on. It is not conditional."]},
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
