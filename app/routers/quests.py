"""Quest management: create, track progress, clear."""

from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.deps import CurrentPlayer, DbDep, SettingsDep
from app.errors import ValidationError
from app.models import Quest, QuestInstance, QuestStatus, QuestType
from app.schemas.quest import (
    ProgressRequest,
    QuestActionResponse,
    QuestCreate,
    QuestInstanceResponse,
    QuestResponse,
    QuestUpdate,
)
from app.services import clock
from app.services.quests import (
    add_progress,
    complete_instance,
    create_quest,
    current_instance,
    get_quest,
    list_quests,
)

router = APIRouter(prefix="/quests", tags=["quests"])


def _to_response(db, quest: Quest, player) -> QuestResponse:
    """Serialize a quest together with the instance the player acts on now."""
    response = QuestResponse.model_validate(quest)
    instance = current_instance(db, quest, player=player)
    if instance is not None:
        response.current_instance = QuestInstanceResponse.model_validate(instance)
    return response


@router.post(
    "",
    response_model=QuestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept a new quest",
)
def create(
    payload: QuestCreate, player: CurrentPlayer, db: DbDep
) -> QuestResponse:
    """Create a quest. Its first instance opens immediately for today."""
    quest = create_quest(
        db,
        player,
        title=payload.title,
        description=payload.description,
        quest_type=payload.quest_type,
        difficulty=payload.difficulty,
        target_count=payload.target_count,
        unit=payload.unit,
        exp_reward=payload.exp_reward,
        stat_reward=payload.stat_reward,
        stat_reward_amount=payload.stat_reward_amount,
    )
    db.commit()
    return _to_response(db, quest, player)


@router.get("", response_model=list[QuestResponse], summary="List quests")
def index(
    player: CurrentPlayer,
    db: DbDep,
    quest_type: QuestType | None = Query(default=None),
    include_archived: bool = Query(default=False),
) -> list[QuestResponse]:
    quests = list_quests(
        db, player, quest_type=quest_type, include_archived=include_archived
    )
    return [_to_response(db, quest, player) for quest in quests]


@router.get("/today", response_model=list[QuestResponse], summary="Today's daily quests")
def today(player: CurrentPlayer, db: DbDep) -> list[QuestResponse]:
    """The active daily quests for the player's current local date.

    Call POST /system/daily-reset first if the app has been closed overnight;
    this endpoint reports state, it does not roll the day over.
    """
    local_today = clock.local_date(player.timezone)

    instances = db.scalars(
        select(QuestInstance)
        .join(Quest, Quest.id == QuestInstance.quest_id)
        .where(
            QuestInstance.player_id == player.id,
            QuestInstance.quest_date == local_today,
            Quest.quest_type == QuestType.DAILY,
            Quest.is_active.is_(True),
        )
        .order_by(QuestInstance.id)
    ).all()

    responses = []
    for instance in instances:
        quest = db.get(Quest, instance.quest_id)
        if quest is None:
            continue
        response = QuestResponse.model_validate(quest)
        response.current_instance = QuestInstanceResponse.model_validate(instance)
        responses.append(response)
    return responses


@router.get("/{quest_id}", response_model=QuestResponse, summary="Fetch one quest")
def show(quest_id: int, player: CurrentPlayer, db: DbDep) -> QuestResponse:
    return _to_response(db, get_quest(db, player, quest_id), player)


@router.patch("/{quest_id}", response_model=QuestResponse, summary="Edit a quest")
def update(
    quest_id: int, payload: QuestUpdate, player: CurrentPlayer, db: DbDep
) -> QuestResponse:
    """Edit a quest definition.

    Changing target_count also updates today's open instance, so the change
    takes effect now rather than tomorrow. Instances already resolved keep the
    target they were judged against.
    """
    quest = get_quest(db, player, quest_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(quest, field, value)

    if payload.target_count is not None:
        instance = current_instance(db, quest, player=player)
        if instance is not None and instance.status is QuestStatus.ACTIVE:
            instance.target_count = payload.target_count

    db.commit()
    return _to_response(db, quest, player)


@router.delete(
    "/{quest_id}",
    response_model=QuestResponse,
    summary="Archive a quest",
)
def archive(quest_id: int, player: CurrentPlayer, db: DbDep) -> QuestResponse:
    """Archive a quest: it stops spawning instances but keeps its history.

    Deliberately not a hard delete — the completed instances behind a quest are
    the record of work already done. Reactivate with PATCH is_active=true.
    """
    quest = get_quest(db, player, quest_id)
    quest.is_active = False
    db.commit()
    return _to_response(db, quest, player)


@router.post(
    "/{quest_id}/progress",
    response_model=QuestActionResponse,
    summary="Log progress",
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
    instance = current_instance(db, quest, player=player)
    if instance is None:
        raise ValidationError(
            "This quest has no open instance for today. "
            "Run POST /system/daily-reset to issue today's quests."
        )

    exp_before = player.total_exp_earned
    level_before = player.level

    instance, completed = add_progress(
        db, player, quest, instance, payload.amount, settings
    )
    db.commit()

    return QuestActionResponse(
        quest=_to_response(db, quest, player),
        instance=QuestInstanceResponse.model_validate(instance),
        completed=completed,
        exp_gained=player.total_exp_earned - exp_before,
        leveled_up=player.level > level_before,
    )


@router.post(
    "/{quest_id}/complete",
    response_model=QuestActionResponse,
    summary="Clear a quest outright",
)
def complete(
    quest_id: int,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> QuestActionResponse:
    """Mark the quest cleared regardless of logged progress, and pay its rewards."""
    quest = get_quest(db, player, quest_id)
    instance = current_instance(db, quest, player=player)
    if instance is None:
        raise ValidationError(
            "This quest has no open instance for today. "
            "Run POST /system/daily-reset to issue today's quests."
        )

    exp_before = player.total_exp_earned
    level_before = player.level

    complete_instance(db, player, quest, instance, settings)
    db.commit()

    return QuestActionResponse(
        quest=_to_response(db, quest, player),
        instance=QuestInstanceResponse.model_validate(instance),
        completed=True,
        exp_gained=player.total_exp_earned - exp_before,
        leveled_up=player.level > level_before,
    )
