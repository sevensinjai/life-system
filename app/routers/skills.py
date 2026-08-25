"""Designing the skill graph and training it."""

from fastapi import APIRouter, Query, status

from app.config import Settings
from app.deps import CurrentPlayer, DbDep, SettingsDep
from app.models import Skill
from app.schemas.skill import (
    PracticeRequest,
    PracticeResponse,
    SkillAwardResponse,
    SkillCreate,
    SkillDetail,
    SkillNode,
    SkillResponse,
    SkillUpdate,
)
from app.services import skills as skill_service
from app.services.skills import TreeNode

router = APIRouter(prefix="/skills", tags=["skills"])


def _to_response(skill: Skill, settings: Settings, depth: int) -> SkillResponse:
    """Project a skill, filling in the derived progression fields."""
    to_next = skill_service.exp_to_next(skill, settings)
    return SkillResponse(
        id=skill.id,
        parent_id=skill.parent_id,
        name=skill.name,
        description=skill.description,
        level=skill.level,
        exp=skill.exp,
        exp_to_next_level=to_next,
        exp_progress=round(skill.exp / to_next, 4) if to_next > 0 else 1.0,
        total_exp_earned=skill.total_exp_earned,
        is_active=skill.is_active,
        depth=depth,
        created_at=skill.created_at,
    )


def _to_node(node: TreeNode, settings: Settings) -> SkillNode:
    return SkillNode(
        **_to_response(node.skill, settings, node.depth).model_dump(),
        children=[_to_node(child, settings) for child in node.children],
    )


def _depth(db, player, skill: Skill) -> int:
    return skill_service.depth_of(skill_service.parent_map(db, player), skill.id)


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill",
)
def create(
    payload: SkillCreate, player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> SkillResponse:
    """Add a skill, on its own or beneath one you already have.

    Skills start at Level 1 with no EXP; they advance when a quest that names
    them is cleared, or when you log practice against them.
    """
    skill = skill_service.create_skill(
        db,
        player,
        settings,
        name=payload.name,
        description=payload.description,
        parent_id=payload.parent_id,
    )
    db.commit()
    return _to_response(skill, settings, _depth(db, player, skill))


@router.get("", response_model=list[SkillNode], summary="Your skill graph")
def index(
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
    include_archived: bool = Query(default=False),
) -> list[SkillNode]:
    """The whole graph, nested, top-level skills first.

    Archived skills are left out by default. Asking for them puts them back in
    place rather than listing them separately, so the shape stays recognizable.
    """
    rows = skill_service.list_skills(db, player, include_archived=include_archived)
    return [
        _to_node(node, settings) for node in skill_service.build_forest(rows)
    ]


@router.get("/{skill_id}", response_model=SkillDetail, summary="Fetch one skill")
def show(
    skill_id: int, player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> SkillDetail:
    """One skill, with the trail down to it and the level directly beneath."""
    skill = skill_service.get_skill(db, player, skill_id)
    parents = skill_service.parent_map(db, player)

    ancestors = skill_service.ancestor_ids(parents, skill.id)
    by_id = {
        node.id: node
        for node in skill_service.list_skills(db, player, include_archived=True)
    }

    path = [
        _to_response(by_id[node_id], settings, depth)
        # ancestor_ids runs nearest-first; a breadcrumb reads root-first.
        for depth, node_id in enumerate(reversed(ancestors), start=1)
        if node_id in by_id
    ]
    depth = len(ancestors) + 1
    children = [
        _to_response(node, settings, depth + 1)
        for node in by_id.values()
        if node.parent_id == skill.id
    ]

    return SkillDetail(
        **_to_response(skill, settings, depth).model_dump(),
        path=path,
        children=children,
    )


@router.patch("/{skill_id}", response_model=SkillResponse, summary="Edit a skill")
def update(
    skill_id: int,
    payload: SkillUpdate,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> SkillResponse:
    """Rename a skill, describe it, move it, or archive and restore it.

    Moving a skill takes its whole subtree along. A move that would make a
    skill its own ancestor, or push a branch past the depth limit, is
    rejected — the graph is never left in a shape it could not be authored in.
    """
    skill = skill_service.get_skill(db, player, skill_id)
    fields = payload.model_fields_set

    if payload.name is not None:
        skill.name = skill_service.rename(db, player, skill, payload.name)
    if "description" in fields:
        skill.description = payload.description
    if "parent_id" in fields:
        skill_service.reparent(db, player, skill, settings, payload.parent_id)
    if payload.is_active is not None:
        skill_service.set_active(db, player, skill, payload.is_active)

    db.commit()
    return _to_response(skill, settings, _depth(db, player, skill))


@router.delete(
    "/{skill_id}", response_model=list[SkillResponse], summary="Archive a skill"
)
def archive(
    skill_id: int, player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> list[SkillResponse]:
    """Archive a skill and everything under it.

    Not a hard delete: the EXP banked in a branch is a record of work done.
    Returns every skill the archive touched, so the client can update the
    whole subtree without refetching. Restore with PATCH is_active=true.
    """
    skill = skill_service.get_skill(db, player, skill_id)
    affected = skill_service.set_active(db, player, skill, False)
    db.commit()

    parents = skill_service.parent_map(db, player)
    return [
        _to_response(node, settings, skill_service.depth_of(parents, node.id))
        for node in affected
    ]


@router.post(
    "/{skill_id}/practice",
    response_model=PracticeResponse,
    summary="Log practice",
)
def practice(
    skill_id: int,
    payload: PracticeRequest,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> PracticeResponse:
    """Credit practice that no quest covers.

    The EXP lands on this skill and rolls up the branch above it, so training
    a sub-skill advances the skill it belongs to.
    """
    skill = skill_service.get_skill(db, player, skill_id)
    awards = skill_service.practice(db, player, skill, payload.exp, settings)
    db.commit()

    return PracticeResponse(
        skill=_to_response(skill, settings, _depth(db, player, skill)),
        awards=SkillAwardResponse.from_awards(awards),
    )
