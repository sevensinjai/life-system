"""Quest authoring and tracking."""

from datetime import date

from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import CurrentPlayer, DbDep, SettingsDep
from app.errors import ValidationError
from app.models import Player, Quest, QuestInstance, QuestStatus, ScheduleKind
from app.schemas.skill import SkillAwardResponse
from app.schemas.quest import (
    ProgressRequest,
    QuestActionResponse,
    QuestCreate,
    QuestInstanceResponse,
    QuestResponse,
    QuestUpdate,
    ScheduleResponse,
    ScheduleSpec,
)
from app.services import clock, scheduling
from app.services.quests import (
    add_progress,
    build_schedule,
    complete_instance,
    create_quest,
    current_instance,
    get_quest,
    list_quests,
    next_due_date,
    resolve_skill_reward,
    schedule_of,
)

router = APIRouter(prefix="/quests", tags=["quests"])


def _schedule_response(quest: Quest) -> ScheduleResponse:
    schedule = schedule_of(quest)
    return ScheduleResponse(
        kind=quest.schedule,
        days=quest.schedule_days,
        interval_days=quest.schedule_interval_days,
        anchor=quest.schedule_anchor,
        week_start=quest.week_start,
        label=scheduling.describe(schedule),
    )


def _build_response(
    quest: Quest, instance: QuestInstance | None, today: date
) -> QuestResponse:
    """Assemble a quest response.

    Built field by field rather than from attributes: `schedule` is a flat
    enum on the model but a nested object in the response, so the two shapes
    do not line up for automatic validation.
    """
    return QuestResponse(
        id=quest.id,
        title=quest.title,
        description=quest.description,
        schedule=_schedule_response(quest),
        difficulty=quest.difficulty,
        target_count=quest.target_count,
        unit=quest.unit,
        exp_reward=quest.exp_reward,
        stat_reward=quest.stat_reward,
        stat_reward_amount=quest.stat_reward_amount,
        skill_id=quest.skill_id,
        skill_exp_reward=quest.skill_exp_reward,
        is_active=quest.is_active,
        created_at=quest.created_at,
        current_instance=(
            QuestInstanceResponse.model_validate(instance) if instance else None
        ),
        next_due_date=next_due_date(quest, today),
    )


def _to_response(
    db: Session, quest: Quest, player: Player, today: date | None = None
) -> QuestResponse:
    """Serialize a quest with its open period and its next due date."""
    today = today or clock.local_date(player.timezone)
    instance = current_instance(db, quest, today=today, player=player)
    return _build_response(quest, instance, today)


def _schedule_from(spec: ScheduleSpec):
    return build_schedule(
        spec.kind,
        days=spec.days,
        interval_days=spec.interval_days,
        anchor=spec.anchor,
        week_start=spec.week_start,
    )


@router.post(
    "",
    response_model=QuestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Author a new quest",
)
def create(payload: QuestCreate, player: CurrentPlayer, db: DbDep) -> QuestResponse:
    """Design a quest and put it on your board.

    Its first period opens immediately if the schedule falls on today;
    otherwise the reset opens one when it comes due.
    """
    quest = create_quest(
        db,
        player,
        title=payload.title,
        description=payload.description,
        schedule=_schedule_from(payload.schedule),
        difficulty=payload.difficulty,
        target_count=payload.target_count,
        unit=payload.unit,
        exp_reward=payload.exp_reward,
        stat_reward=payload.stat_reward,
        stat_reward_amount=payload.stat_reward_amount,
        skill_id=payload.skill_id,
        skill_exp_reward=payload.skill_exp_reward,
    )
    db.commit()
    return _to_response(db, quest, player)


@router.get("", response_model=list[QuestResponse], summary="List authored quests")
def index(
    player: CurrentPlayer,
    db: DbDep,
    schedule: ScheduleKind | None = Query(
        default=None, description="Filter to one schedule kind."
    ),
    recurring_only: bool = Query(
        default=False, description="Exclude one-time quests."
    ),
    include_archived: bool = Query(default=False),
) -> list[QuestResponse]:
    quests = list_quests(
        db,
        player,
        schedule=schedule,
        recurring_only=recurring_only,
        include_archived=include_archived,
    )
    today = clock.local_date(player.timezone)
    return [_to_response(db, quest, player, today) for quest in quests]


@router.get(
    "/today", response_model=list[QuestResponse], summary="What is on the board today"
)
def today(player: CurrentPlayer, db: DbDep) -> list[QuestResponse]:
    """Every quest with a period open right now.

    Includes a weekly quest mid-week and a one-time quest still outstanding —
    anything you could make progress on today. Call POST /system/daily-reset
    first if the app has been closed; this endpoint reports state, it does not
    roll periods over.
    """
    local_today = clock.local_date(player.timezone)

    instances = db.scalars(
        select(QuestInstance)
        .join(Quest, Quest.id == QuestInstance.quest_id)
        .where(
            QuestInstance.player_id == player.id,
            QuestInstance.status == QuestStatus.ACTIVE,
            QuestInstance.period_start <= local_today,
            (QuestInstance.period_end.is_(None))
            | (QuestInstance.period_end >= local_today),
            Quest.is_active.is_(True),
        )
        .order_by(QuestInstance.period_end.is_(None), QuestInstance.period_end)
    ).all()

    responses = []
    for instance in instances:
        quest = db.get(Quest, instance.quest_id)
        if quest is None:
            continue
        responses.append(_build_response(quest, instance, local_today))
    return responses


@router.get("/{quest_id}", response_model=QuestResponse, summary="Fetch one quest")
def show(quest_id: int, player: CurrentPlayer, db: DbDep) -> QuestResponse:
    return _to_response(db, get_quest(db, player, quest_id), player)


@router.patch("/{quest_id}", response_model=QuestResponse, summary="Redesign a quest")
def update(
    quest_id: int, payload: QuestUpdate, player: CurrentPlayer, db: DbDep
) -> QuestResponse:
    """Edit a quest you authored.

    Changing target_count also updates the open period, so the change applies
    now rather than next time. Periods already resolved keep the target they
    were judged against.

    Changing the schedule takes effect from the next period onward; the open
    one is left alone rather than retroactively re-dated.
    """
    quest = get_quest(db, player, quest_id)

    fields = payload.model_dump(exclude_unset=True)
    schedule_spec = fields.pop("schedule", None)

    # The skill link is settled together: an amount is only meaningful
    # alongside the skill it pays, and either may be the one being changed.
    if "skill_id" in fields or "skill_exp_reward" in fields:
        skill_id = fields.pop("skill_id", quest.skill_id)
        given = fields.pop("skill_exp_reward", None)
        quest.skill_id = skill_id
        quest.skill_exp_reward = resolve_skill_reward(
            db,
            player,
            skill_id,
            given if given is not None else (quest.skill_exp_reward or None),
            payload.exp_reward if payload.exp_reward is not None else quest.exp_reward,
        )

    for field, value in fields.items():
        setattr(quest, field, value)

    if schedule_spec is not None:
        schedule = _schedule_from(payload.schedule)
        quest.schedule = schedule.kind
        quest.schedule_days = list(schedule.days) or None
        quest.schedule_interval_days = schedule.interval_days
        quest.week_start = schedule.week_start
        # Keep the original anchor unless the author sets a new one, so an
        # interval quest does not silently restart its cycle on every edit.
        if schedule.anchor is not None:
            quest.schedule_anchor = schedule.anchor
        elif quest.schedule_anchor is None:
            quest.schedule_anchor = clock.local_date(player.timezone)

    if payload.target_count is not None:
        instance = current_instance(db, quest, player=player)
        if instance is not None and instance.status is QuestStatus.ACTIVE:
            instance.target_count = payload.target_count

    db.commit()
    return _to_response(db, quest, player)


@router.delete("/{quest_id}", response_model=QuestResponse, summary="Archive a quest")
def archive(quest_id: int, player: CurrentPlayer, db: DbDep) -> QuestResponse:
    """Archive a quest: it stops spawning periods but keeps its history.

    Deliberately not a hard delete — the cleared periods behind a quest are the
    record of work already done. Reactivate with PATCH is_active=true.
    """
    quest = get_quest(db, player, quest_id)
    quest.is_active = False
    db.commit()
    return _to_response(db, quest, player)


def _open_instance_or_422(db: Session, quest: Quest, player: Player) -> QuestInstance:
    instance = current_instance(db, quest, player=player)
    if instance is None:
        raise ValidationError(
            "This quest has no open period right now. Its schedule "
            f"({scheduling.describe(schedule_of(quest))}) does not fall on today, "
            "or POST /system/daily-reset has not run yet."
        )
    return instance


@router.post(
    "/{quest_id}/progress", response_model=QuestActionResponse, summary="Log progress"
)
def progress(
    quest_id: int,
    payload: ProgressRequest,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> QuestActionResponse:
    """Add units of progress; the quest clears automatically at its target."""
    quest = get_quest(db, player, quest_id)
    instance = _open_instance_or_422(db, quest, player)

    exp_before = player.total_exp_earned
    level_before = player.level

    instance, completed, skill_awards = add_progress(
        db, player, quest, instance, payload.amount, settings
    )
    db.commit()

    return QuestActionResponse(
        quest=_to_response(db, quest, player),
        instance=QuestInstanceResponse.model_validate(instance),
        completed=completed,
        exp_gained=player.total_exp_earned - exp_before,
        leveled_up=player.level > level_before,
        skill_awards=SkillAwardResponse.from_awards(skill_awards),
    )


@router.post(
    "/{quest_id}/complete",
    response_model=QuestActionResponse,
    summary="Clear a quest outright",
)
def complete(
    quest_id: int, player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> QuestActionResponse:
    """Mark the open period cleared regardless of logged progress."""
    quest = get_quest(db, player, quest_id)
    instance = _open_instance_or_422(db, quest, player)

    exp_before = player.total_exp_earned
    level_before = player.level

    _, skill_awards = complete_instance(db, player, quest, instance, settings)
    db.commit()

    return QuestActionResponse(
        quest=_to_response(db, quest, player),
        instance=QuestInstanceResponse.model_validate(instance),
        completed=True,
        exp_gained=player.total_exp_earned - exp_before,
        leveled_up=player.level > level_before,
        skill_awards=SkillAwardResponse.from_awards(skill_awards),
    )
