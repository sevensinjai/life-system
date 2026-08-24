"""Request and response models for the player's status window."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import StatName


class StatBlock(BaseModel):
    strength: int
    agility: int
    vitality: int
    intelligence: int
    perception: int


class PlayerStatus(BaseModel):
    """The status window: everything the app shows on the main screen."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    level: int
    exp: int = Field(description="EXP toward the next level, not a lifetime total.")
    exp_to_next_level: int
    exp_progress: float = Field(description="Fraction of the way to the next level, 0-1.")
    total_exp_earned: int
    stat_points: int = Field(description="Unspent points awaiting allocation.")
    stats: StatBlock
    timezone: str


class AllocateStatsRequest(BaseModel):
    """Spend stat points. Omitted stats receive nothing."""

    strength: int = Field(default=0, ge=0)
    agility: int = Field(default=0, ge=0)
    vitality: int = Field(default=0, ge=0)
    intelligence: int = Field(default=0, ge=0)
    perception: int = Field(default=0, ge=0)

    def as_allocations(self) -> dict[StatName, int]:
        return {
            StatName.STRENGTH: self.strength,
            StatName.AGILITY: self.agility,
            StatName.VITALITY: self.vitality,
            StatName.INTELLIGENCE: self.intelligence,
            StatName.PERCEPTION: self.perception,
        }


class UpdatePlayerRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    timezone: str | None = Field(default=None, max_length=64)
