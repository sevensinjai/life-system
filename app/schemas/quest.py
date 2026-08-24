"""Request and response models for quests."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import QuestDifficulty, QuestStatus, QuestType, StatName


class QuestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    quest_type: QuestType = QuestType.NORMAL
    difficulty: QuestDifficulty = QuestDifficulty.E
    target_count: int = Field(default=1, ge=1, description="Units needed to clear it.")
    unit: str | None = Field(default=None, max_length=32, examples=["push-ups", "pages"])
    exp_reward: int | None = Field(
        default=None, ge=0, description="Defaults to the difficulty's standard reward."
    )
    stat_reward: StatName | None = None
    stat_reward_amount: int = Field(default=0, ge=0)


class QuestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    difficulty: QuestDifficulty | None = None
    target_count: int | None = Field(default=None, ge=1)
    unit: str | None = Field(default=None, max_length=32)
    exp_reward: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class QuestInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quest_id: int
    quest_date: date
    progress: int
    target_count: int
    status: QuestStatus
    completed_at: datetime | None


class QuestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    quest_type: QuestType
    difficulty: QuestDifficulty
    target_count: int
    unit: str | None
    exp_reward: int
    stat_reward: StatName | None
    stat_reward_amount: int
    is_active: bool
    created_at: datetime
    current_instance: QuestInstanceResponse | None = None


class ProgressRequest(BaseModel):
    amount: int = Field(
        default=1,
        description="Units to add. Negative corrects an over-count; zero is rejected.",
    )


class QuestActionResponse(BaseModel):
    """A quest action's result, bundled with the status window it produced.

    The client needs both after a completion: the quest's new state and the
    level or EXP change it caused. Returning them together avoids a second
    round trip on the critical path.
    """

    quest: QuestResponse
    instance: QuestInstanceResponse
    completed: bool
    exp_gained: int = 0
    leveled_up: bool = False
