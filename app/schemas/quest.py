"""Request and response models for authoring and running quests."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import QuestDifficulty, QuestStatus, ScheduleKind, StatName
from app.schemas.skill import SkillAwardResponse
from app.services.scheduling import MAX_INTERVAL_DAYS


class ScheduleSpec(BaseModel):
    """How often a quest comes around.

    Which fields apply depends on `kind`:

    - `once` — no recurrence; the quest waits until you clear it
    - `daily` — a new one-day period every day
    - `weekdays` — needs `days`, e.g. `[0, 2, 4]` for Mon/Wed/Fri
    - `interval` — needs `interval_days`; you get the whole window to finish
    - `weekly` — one seven-day period per week, optionally set `week_start`

    "Three runs a week" is a `weekly` quest with `target_count: 3`.
    """

    kind: ScheduleKind = ScheduleKind.ONCE
    days: list[int] | None = Field(
        default=None,
        description="Weekdays for a `weekdays` schedule; 0 is Monday, 6 is Sunday.",
        examples=[[0, 2, 4]],
    )
    interval_days: int | None = Field(
        default=None,
        ge=1,
        le=MAX_INTERVAL_DAYS,
        description="Period length for an `interval` schedule.",
    )
    anchor: date | None = Field(
        default=None,
        description="The day the recurrence counts from. Defaults to today.",
    )
    week_start: int = Field(
        default=0, ge=0, le=6, description="Which weekday a `weekly` period opens on."
    )

    @field_validator("days")
    @classmethod
    def _check_days(cls, days: list[int] | None) -> list[int] | None:
        if days is None:
            return None
        if any(not 0 <= day <= 6 for day in days):
            raise ValueError("Weekdays must be between 0 (Monday) and 6 (Sunday).")
        return sorted(set(days))


class QuestCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    schedule: ScheduleSpec = Field(default_factory=ScheduleSpec)
    difficulty: QuestDifficulty = QuestDifficulty.E
    target_count: int = Field(
        default=1, ge=1, description="Units needed to clear one period."
    )
    unit: str | None = Field(default=None, max_length=32, examples=["push-ups", "runs"])
    exp_reward: int | None = Field(
        default=None, ge=0, description="Defaults to the difficulty's standard reward."
    )
    stat_reward: StatName | None = None
    stat_reward_amount: int = Field(default=0, ge=0)
    skill_id: int | None = Field(
        default=None, description="Clearing this quest trains this skill."
    )
    skill_exp_reward: int | None = Field(
        default=None,
        ge=0,
        description=(
            "EXP the linked skill earns. Defaults to the quest's own EXP "
            "reward when a skill is named and no amount is given."
        ),
    )


class QuestUpdate(BaseModel):
    """Edit a quest. Omitted fields are left alone."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    schedule: ScheduleSpec | None = None
    difficulty: QuestDifficulty | None = None
    target_count: int | None = Field(default=None, ge=1)
    unit: str | None = Field(default=None, max_length=32)
    exp_reward: int | None = Field(default=None, ge=0)
    stat_reward: StatName | None = None
    stat_reward_amount: int | None = Field(default=None, ge=0)
    skill_id: int | None = None
    skill_exp_reward: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class QuestInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quest_id: int
    period_start: date
    period_end: date | None = Field(
        description="Last day to finish. Null for a one-time quest, which never lapses."
    )
    progress: int
    target_count: int
    status: QuestStatus
    completed_at: datetime | None


class ScheduleResponse(BaseModel):
    """A quest's schedule as stored, plus a label ready to display."""

    kind: ScheduleKind
    days: list[int] | None
    interval_days: int | None
    anchor: date | None
    week_start: int
    label: str = Field(examples=["Every Mon, Wed, Fri"])


class QuestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    schedule: ScheduleResponse
    difficulty: QuestDifficulty
    target_count: int
    unit: str | None
    exp_reward: int
    stat_reward: StatName | None
    stat_reward_amount: int
    skill_id: int | None = None
    skill_exp_reward: int = 0
    is_active: bool
    created_at: datetime
    current_instance: QuestInstanceResponse | None = Field(
        default=None,
        description="The open period, if the quest is due right now.",
    )
    next_due_date: date | None = Field(
        default=None, description="When the next period opens. Null for a one-time quest."
    )


class ProgressRequest(BaseModel):
    amount: int = Field(
        default=1,
        description="Units to add. Negative corrects an over-count; zero is rejected.",
    )


class QuestActionResponse(BaseModel):
    """A quest action's result, bundled with the progression it caused.

    The client needs both after a completion: the quest's new state and the
    level or EXP change. Returning them together avoids a second round trip
    on the critical path.
    """

    quest: QuestResponse
    instance: QuestInstanceResponse
    completed: bool
    exp_gained: int = 0
    leveled_up: bool = False
    skill_awards: list[SkillAwardResponse] = Field(
        default_factory=list,
        description=(
            "Skills credited by this action: the one the quest names, then "
            "each skill above it. Empty when the quest trains nothing."
        ),
    )
