"""Request and response models for side quests and the opt-in that gates them."""

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.models.enums import (
    QuestDifficulty,
    SideQuestFrequency,
    SideQuestOfferStatus,
    SideQuestStatus,
    StatName,
)
from app.services.clock import as_utc

# Side quest windows are absolute instants, and a client that reads a deadline
# as local time is wrong by hours. SQLite hands stored timestamps back without
# a timezone, so every datetime leaving this module is stamped UTC on the way
# out rather than trusting whatever the backend returned.
UtcMoment = Annotated[datetime, AfterValidator(as_utc)]


class SideQuestPreferenceUpdate(BaseModel):
    """Answer the opt-in question. Omitted fields are left alone."""

    is_opted_in: bool | None = Field(
        default=None,
        description=(
            "Whether the System may send you side quests at all. "
            "Off until you turn it on."
        ),
    )
    frequency: SideQuestFrequency | None = Field(
        default=None,
        description=(
            "How much of the broadcast traffic reaches you: rare is one a "
            "week, occasional three, frequent up to seven."
        ),
    )
    max_difficulty: QuestDifficulty | None = Field(
        default=None,
        description=(
            "The hardest rank you are willing to be sent. Send null to lift "
            "the cap and take anything."
        ),
    )
    auto_accept: bool | None = Field(
        default=None,
        description=(
            "Accept side quests without being asked. Note that an accepted "
            "side quest can carry a penalty if you let it lapse."
        ),
    )


class SideQuestPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_opted_in: bool
    frequency: SideQuestFrequency
    max_difficulty: QuestDifficulty | None
    auto_accept: bool
    offers_per_week: int = Field(
        description="How many offers your frequency allows through in a week."
    )
    offers_this_week: int = Field(
        description="How many you have already received in the last seven days."
    )
    open_offers: int = Field(
        description="Side quests currently waiting on you or in progress."
    )
    opted_in_at: UtcMoment | None = None
    opted_out_at: UtcMoment | None = None


class SideQuestResponse(BaseModel):
    """The broadcast itself — the same for every player who received it."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    herald: str | None = Field(
        description="Who issued it, if the System named itself."
    )
    difficulty: QuestDifficulty
    target_count: int
    unit: str | None
    exp_reward: int
    stat_reward: StatName | None
    stat_reward_amount: int
    penalty_exp: int = Field(
        description="EXP charged only for accepting and then not finishing."
    )
    status: SideQuestStatus
    broadcast_at: UtcMoment
    expires_at: UtcMoment | None


class SideQuestOfferResponse(BaseModel):
    """Your copy of a broadcast: the quest, your answer, and your progress."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: SideQuestOfferStatus
    progress: int
    target_count: int
    expires_at: UtcMoment | None
    offered_at: UtcMoment
    responded_at: UtcMoment | None
    completed_at: UtcMoment | None
    side_quest: SideQuestResponse


class SideQuestProgressRequest(BaseModel):
    amount: int = Field(
        description="Units to add. Negative corrects a mis-logged entry."
    )


class SideQuestProgressResponse(BaseModel):
    offer: SideQuestOfferResponse
    completed: bool = Field(description="Whether this call cleared the side quest.")
