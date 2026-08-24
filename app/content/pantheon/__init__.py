"""The constellations: who is watching, and how each of them talks.

Twenty-six figures out of real mythology — Greek, Chinese and Japanese — each
remembered for the thing it now asks of you. Some are names anyone would
recognise; a good many are not, and those are half the point. The pantheon is
split by tradition into modules beside this one, which is also where a
twenty-seventh would go.

Every one carries two names. The **real name** is the figure: 刑天, Hermes,
天照大神. The **code name** is the title it speaks under, taken from its own
story — 「猛志常在」 from the line Tao Yuanming wrote about Xingtian,
「一簞一瓢」 from the passage in the Analects about Yan Hui. The title is what
appears when it speaks; the name underneath is the reminder that it was
somebody.

Written with the respect owed to figures people still honour. They ask for
persistence, restraint, study and attention — the things they are actually
remembered for — and none of them is played for a joke.

The voice is a mapping of *line kind* to *standing* to a list of alternatives:

    {"offer": {"default": ["..."], "favored": ["..."]}}

A missing standing falls back to "default", and a missing kind falls back to
the plain System lines below, so a constellation only has to write the lines
where it actually sounds different from the rest.

Line kinds for a side quest: offer, accept, decline, complete, fail, expire.

Line kinds for a request to be befriended: refuse (it would not hear you this
time), befriend (you cleared its trial), rebuff (you did not), farewell (you
ended it). The trial it sets speaks through its own lines, in
`content/challenges/`.

Interpolation is deliberately absent — a line is a finished sentence, not a
template. Anything the client needs to say alongside it (counts, deadlines,
EXP) is already structured on the event payload, so a line never has to be
parsed or reassembled to be translated.
"""

from typing import Any

from app.content.entries import ConstellationEntry
from app.content.pantheon.chinese import CHINESE
from app.content.pantheon.greek import GREEK
from app.content.pantheon.japanese import JAPANESE

__all__ = [
    "PANTHEON",
    "SYSTEM_VOICE",
    "ConstellationEntry",
    "as_voice_payload",
    "by_code",
]


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


# Order matters a little: it is the order the pantheon is listed in, and a
# player meeting twenty-six of these reads the first few most carefully.
PANTHEON: tuple[ConstellationEntry, ...] = GREEK + CHINESE + JAPANESE


def by_code() -> dict[str, ConstellationEntry]:
    """The pantheon keyed by code, for seeding and for tests."""
    return {entry.code: entry for entry in PANTHEON}


def as_voice_payload(entry: ConstellationEntry) -> dict[str, Any]:
    """The voice as it is stored — a plain JSON-shaped dict."""
    return {
        kind: {standing: list(lines) for standing, lines in bands.items()}
        for kind, bands in entry.voice.items()
    }
