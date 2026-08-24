"""Response models for the pantheon and where the player stands with it."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Standing, StatName


class ConstellationBrief(BaseModel):
    """Enough to put a name to a broadcast."""

    model_config = ConfigDict(from_attributes=True)

    code: str = Field(description="Stable identifier; survives a rename.")
    name: str
    epithet: str | None
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
    first_seen_at: datetime | None = Field(
        default=None, description="When it first sent you something."
    )
    last_seen_at: datetime | None = None


class ConstellationResponse(BaseModel):
    """A constellation, and what it makes of you."""

    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    epithet: str | None
    description: str | None
    domain: StatName | None
    standing: StandingBlock = Field(
        description=(
            "Your history with it. A constellation you have never heard from "
            "reads as a stranger with an empty record."
        )
    )
