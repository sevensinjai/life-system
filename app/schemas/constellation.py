"""Response models for the pantheon and where the player stands with it."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FriendshipStatus, MythTradition, Standing, StatName
from app.schemas.common import UtcMoment


class ConstellationBrief(BaseModel):
    """Enough to put a name to a broadcast.

    Both names, in both scripts, because which to show is the client's call —
    including showing both at once, which is how these are usually written:
    「猛志常在」 The Will That Remains.
    """

    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Stable identifier; survives a rename.")
    tradition: MythTradition = Field(description="Which body of myth it comes from.")
    code_name: str = Field(description="What it is called: a title.")
    code_name_zh_hant: str | None = Field(
        default=None, description="The same title in Traditional Chinese."
    )
    real_name: str | None = Field(
        default=None, description="Who it was before it was a constellation."
    )
    real_name_zh_hant: str | None = Field(
        default=None, description="The same name in Traditional Chinese."
    )
    epithet: str | None
    epithet_zh_hant: str | None = None
    domain: StatName | None = Field(
        description="What it cares about. Null for one that cares about the habit itself."
    )


class StandingBlock(BaseModel):
    """One player's history with one constellation."""

    standing: Standing = Field(
        description="The band your favor falls into, from forsaken to champion."
    )
    favor: int = Field(description="The running score behind the band.")
    offers_received: int
    completed: int
    declined: int
    expired: int
    failed: int
    first_seen_at: UtcMoment | None = Field(
        default=None, description="When it first sent you something."
    )
    last_seen_at: UtcMoment | None = None


class FriendshipBlock(BaseModel):
    """Whether this constellation issues to you, and what asking would do."""

    is_friend: bool
    befriended_at: UtcMoment | None = None
    may_ask: bool = Field(
        description="Whether a request would be considered right now."
    )
    blocked_by: str | None = Field(
        default=None,
        description=(
            "Why not, when it would not: already_friends, request_open, "
            "too_soon, or retired."
        ),
    )
    retry_after: UtcMoment | None = Field(
        default=None, description="The earliest you may ask again."
    )
    request_status: FriendshipStatus | None = Field(
        default=None, description="How your most recent request ended, if any."
    )
    challenge_offer_id: int | None = Field(
        default=None,
        description="The trial of admission awaiting you, if one was set.",
    )


class FriendshipRequestBody(BaseModel):
    """Ask a constellation to befriend you."""

    message: str | None = Field(
        default=None,
        max_length=1000,
        description=(
            "What you want to say for yourself. Kept with the request; "
            "nothing weighs it yet."
        ),
    )


class FriendshipRequestResponse(BaseModel):
    """The constellation's answer, given at once."""

    status: FriendshipStatus = Field(
        description="`challenged` if it set you a trial, `refused` if it would not hear you."
    )
    constellation: str
    line: str | None = Field(description="What it said.")
    retry_after: UtcMoment | None = Field(
        default=None, description="Set on a refusal: the earliest you may ask again."
    )
    challenge_offer_id: int | None = Field(
        default=None,
        description=(
            "Set on a challenge: the side quest offer to clear. It behaves "
            "like any other — accept it, log progress, complete it."
        ),
    )


class ConstellationResponse(BaseModel):
    """A constellation, and what it makes of you."""

    model_config = ConfigDict(from_attributes=True)

    code: str
    tradition: MythTradition
    code_name: str
    code_name_zh_hant: str | None = None
    real_name: str | None = None
    real_name_zh_hant: str | None = None
    epithet: str | None
    epithet_zh_hant: str | None = None
    description: str | None = Field(
        default=None, description="English only, until the localization pass."
    )
    domain: StatName | None
    standing: StandingBlock = Field(
        description=(
            "Your history with it. A constellation you have never heard from "
            "reads as a stranger with an empty record."
        )
    )
    friendship: FriendshipBlock = Field(
        description="Whether it issues to you, and whether you may ask it to."
    )
