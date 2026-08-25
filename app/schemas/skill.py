"""Request and response models for the skill graph."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.services.skills import MAX_NAME_LENGTH


class SkillCreate(BaseModel):
    name: str = Field(
        min_length=1, max_length=MAX_NAME_LENGTH, examples=["Pitch accuracy"]
    )
    description: str | None = None
    parent_id: int | None = Field(
        default=None,
        description="Nest this skill under another. Omit for a top-level skill.",
    )


class SkillUpdate(BaseModel):
    """Edit a skill. Omitted fields are left alone.

    Sending `parent_id: null` explicitly moves the skill to the top level;
    omitting the field leaves it where it is.
    """

    name: str | None = Field(default=None, min_length=1, max_length=MAX_NAME_LENGTH)
    description: str | None = None
    parent_id: int | None = None
    is_active: bool | None = Field(
        default=None,
        description=(
            "False archives the skill and everything under it; true restores "
            "it along with its ancestors."
        ),
    )


class SkillResponse(BaseModel):
    """One skill, without its children."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int | None
    name: str
    description: str | None
    level: int
    exp: int = Field(description="EXP toward the next level, not a lifetime total.")
    exp_to_next_level: int
    exp_progress: float = Field(description="Fraction of the way to the next level, 0-1.")
    total_exp_earned: int
    is_active: bool
    depth: int = Field(description="1 for a top-level skill.")
    created_at: datetime


class SkillNode(SkillResponse):
    """A skill with its subtree nested inside it."""

    children: list["SkillNode"] = Field(default_factory=list)


SkillNode.model_rebuild()


class SkillDetail(SkillResponse):
    """One skill, with the branch above and below it.

    `path` is the trail from the root down to this skill, which is what a
    breadcrumb renders; `children` is only the immediate level below.
    """

    path: list[SkillResponse] = Field(default_factory=list)
    children: list[SkillResponse] = Field(default_factory=list)


class PracticeRequest(BaseModel):
    exp: int = Field(
        gt=0,
        examples=[50],
        description="EXP earned by this session. Rolls up to the parent skills.",
    )


class SkillAwardResponse(BaseModel):
    """One skill's share of a practice session or a cleared quest."""

    skill_id: int
    name: str
    exp_gained: int
    level: int
    levels_gained: int
    leveled_up: bool
    distance: int = Field(
        description="0 for the skill trained, 1 for its parent, and so on."
    )

    @classmethod
    def from_awards(cls, awards) -> list["SkillAwardResponse"]:
        """Project the service's award records, which are plain dataclasses."""
        return [
            cls(
                skill_id=award.skill_id,
                name=award.name,
                exp_gained=award.exp_gained,
                level=award.level,
                levels_gained=award.levels_gained,
                leveled_up=award.leveled_up,
                distance=award.distance,
            )
            for award in awards
        ]


class PracticeResponse(BaseModel):
    """What a practice session did to the branch it sits on."""

    skill: SkillResponse
    awards: list[SkillAwardResponse] = Field(
        description="Every skill credited, the one trained first."
    )
