"""The side quests themselves, as written.

Each entry is a trial one constellation issues, with the mechanical shape it
takes (rank, target, reward, penalty, how long you get) and the announcement
it goes out with. The scheduler in `services/broadcasting.py` picks one of
these and puts it on the calendar; nothing here decides *when*.

Split by tradition into the modules beside this one, and read as one catalog.

A few rules the catalog follows, so that the promises the data structure makes
stay true in the content as well:

* **Most trials carry no penalty.** `penalty_exp` stays zero unless the trial
  is one you would only accept knowingly — and even then it stays well under
  the reward. A side quest is an offer, not a debt.
* **Nothing is unbounded.** Every trial states a target and a window a person
  could actually clear in that window.
* **Nothing needs equipment, money, or anywhere to be.** These go out to
  everybody at once; a trial only one kind of life can clear is not a
  broadcast, it is an exclusion.
"""

from typing import Any

from app.content.broadcasts.chinese import CHINESE_TRIALS
from app.content.broadcasts.greek import GREEK_TRIALS
from app.content.broadcasts.japanese import JAPANESE_TRIALS
from app.content.entries import BroadcastEntry

__all__ = [
    "BROADCASTS",
    "BroadcastEntry",
    "as_lines_payload",
    "by_code",
    "for_constellation",
]

# Order is the rotation order: a fresh install works down this list before
# anything repeats, so the first few are the ones most players meet first.
BROADCASTS: tuple[BroadcastEntry, ...] = (
    GREEK_TRIALS + CHINESE_TRIALS + JAPANESE_TRIALS
)


def by_code() -> dict[str, BroadcastEntry]:
    """The catalog keyed by code."""
    return {entry.code: entry for entry in BROADCASTS}


def for_constellation(code: str) -> tuple[BroadcastEntry, ...]:
    """Everything one constellation has to issue."""
    return tuple(entry for entry in BROADCASTS if entry.constellation == code)


def as_lines_payload(entry: BroadcastEntry) -> dict[str, Any]:
    """This trial's line overrides, as they are stored."""
    return {
        kind: {standing: list(lines) for standing, lines in bands.items()}
        for kind, bands in entry.lines.items()
    }
