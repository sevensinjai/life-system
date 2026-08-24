"""The constellations: who is watching, and how each of them talks.

Six of them, each with a domain it cares about and a voice of its own. The
voice is a mapping of *line kind* to *standing* to a list of alternatives:

    {"offer": {"default": ["..."], "favored": ["..."]}}

A missing standing falls back to "default", and a missing kind falls back to
the plain System lines at the bottom of this module, so a constellation only
has to write the lines where it actually sounds different from the rest.

Line kinds: offer, accept, decline, complete, fail, expire.

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
    """One constellation as written, before it becomes a row."""

    code: str
    name: str
    epithet: str
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
}


PANTHEON: tuple[ConstellationEntry, ...] = (
    ConstellationEntry(
        code="fallen_star",
        name="The Constellation of the Fallen Star",
        epithet="who fell, and stood up anyway",
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
        },
    ),
    ConstellationEntry(
        code="long_road",
        name="The Constellation of the Long Road",
        epithet="who is still walking",
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
        },
    ),
    ConstellationEntry(
        code="empty_bowl",
        name="The Constellation of the Empty Bowl",
        epithet="who is not hungry",
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
        },
    ),
    ConstellationEntry(
        code="silent_library",
        name="The Constellation of the Silent Library",
        epithet="who has read everything and says little",
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
        },
    ),
    ConstellationEntry(
        code="unblinking_eye",
        name="The Constellation of the Unblinking Eye",
        epithet="who has not looked away since",
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
        },
    ),
    ConstellationEntry(
        code="sleepless_lantern",
        name="The Constellation of the Sleepless Lantern",
        epithet="who keeps the light on",
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
