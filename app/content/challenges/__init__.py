"""The trials of admission: what a constellation sets before it calls you a friend.

A constellation issues to its friends and to nobody else, so this is the way
in. You ask; if it agrees to hear you it sets one of these; clearing it makes
you friends. Failing it, declining it, or letting it lapse ends the request
and starts the wait before you may ask again.

One per constellation — every one of them, or that constellation could never
be befriended at all — and each is the smallest true test of what that figure
is remembered for. A first meeting, not a proving ground: they are
deliberately easier than the trials that follow, and none of them carries a
penalty, because a stranger who fails an audition has lost the audition, which
is punishment enough.
"""

from app.content.challenges.chinese import CHINESE_CHALLENGES
from app.content.challenges.greek import GREEK_CHALLENGES
from app.content.challenges.japanese import JAPANESE_CHALLENGES
from app.content.entries import BroadcastEntry

__all__ = ["CHALLENGES", "BroadcastEntry", "challenge_for"]

# Keyed by constellation code. Reuses the broadcast shape, because a challenge
# *is* a side quest — the only difference is that it is addressed to one
# player rather than broadcast to all of them.
CHALLENGES: dict[str, BroadcastEntry] = {
    **GREEK_CHALLENGES,
    **CHINESE_CHALLENGES,
    **JAPANESE_CHALLENGES,
}


def challenge_for(code: str) -> BroadcastEntry | None:
    """The trial this constellation sets, if it has written one."""
    return CHALLENGES.get(code)
