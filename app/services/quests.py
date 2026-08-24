"""Quest lifecycle: creation, progress, completion."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import NotFoundError, ValidationError
from app.models import (
    DIFFICULTY_EXP,
    EventType,
    Player,
    Quest,
    QuestDifficulty,
    QuestInstance,
    QuestStatus,
    QuestType,
    StatName,
)
from app.services import clock
from app.services.progression import award_exp, log_event


def default_exp_for(difficulty: QuestDifficulty) -> int:
    """The EXP a quest of this difficulty is worth unless overridden."""
    return DIFFICULTY_EXP[difficulty]


def create_quest(
    db: Session,
    player: Player,
    *,
    title: str,
    description: str | None = None,
    quest_type: QuestType = QuestType.NORMAL,
    difficulty: QuestDifficulty = QuestDifficulty.E,
    target_count: int = 1,
    unit: str | None = None,
    exp_reward: int | None = None,
    stat_reward: StatName | None = None,
    stat_reward_amount: int = 0,
    today: date | None = None,
) -> Quest:
    """Create a quest and open its first instance for today."""
    if target_count < 1:
        raise ValidationError("target_count must be at least 1.")
    if stat_reward_amount < 0:
        raise ValidationError("stat_reward_amount must be non-negative.")

    quest = Quest(
        player_id=player.id,
        title=title,
        description=description,
        quest_type=quest_type,
        difficulty=difficulty,
        target_count=target_count,
        unit=unit,
        exp_reward=exp_reward if exp_reward is not None else default_exp_for(difficulty),
        stat_reward=stat_reward,
        stat_reward_amount=stat_reward_amount,
    )
    db.add(quest)
    db.flush()  # assign quest.id before building its instance

    today = today or clock.local_date(player.timezone)
    get_or_create_instance(db, quest, today)

    log_event(
        db,
        player,
        EventType.QUEST_CREATED,
        f"New quest accepted: {quest.title}",
        {"quest_id": quest.id, "quest_type": quest.quest_type.value},
    )
    return quest


def get_or_create_instance(
    db: Session, quest: Quest, quest_date: date
) -> QuestInstance:
    """Fetch the quest's instance for a date, creating it if absent.

    Idempotent, which is what lets the daily reset run more than once a day
    without spawning duplicates.
    """
    existing = db.scalar(
        select(QuestInstance).where(
            QuestInstance.quest_id == quest.id,
            QuestInstance.quest_date == quest_date,
        )
    )
    if existing is not None:
        return existing

    instance = QuestInstance(
        quest_id=quest.id,
        player_id=quest.player_id,
        quest_date=quest_date,
        progress=0,
        target_count=quest.target_count,
        status=QuestStatus.ACTIVE,
    )
    db.add(instance)
    db.flush()
    return instance


def get_quest(db: Session, player: Player, quest_id: int) -> Quest:
    """Fetch one of the player's quests, or raise NotFoundError."""
    quest = db.scalar(
        select(Quest).where(Quest.id == quest_id, Quest.player_id == player.id)
    )
    if quest is None:
        raise NotFoundError(f"No quest with id {quest_id}.")
    return quest


def list_quests(
    db: Session,
    player: Player,
    *,
    quest_type: QuestType | None = None,
    include_archived: bool = False,
) -> list[Quest]:
    """List the player's quests, newest first."""
    stmt = select(Quest).where(Quest.player_id == player.id)
    if quest_type is not None:
        stmt = stmt.where(Quest.quest_type == quest_type)
    if not include_archived:
        stmt = stmt.where(Quest.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Quest.created_at.desc(), Quest.id.desc())))


def current_instance(
    db: Session, quest: Quest, today: date | None = None, player: Player | None = None
) -> QuestInstance | None:
    """The instance a player would act on right now.

    Daily quests use today's instance. Normal quests carry a single instance
    that stays open until cleared, so the most recent one is the live one.
    """
    if quest.quest_type is QuestType.DAILY:
        today = today or clock.local_date(player.timezone if player else "UTC")
        return db.scalar(
            select(QuestInstance).where(
                QuestInstance.quest_id == quest.id,
                QuestInstance.quest_date == today,
            )
        )
    return db.scalar(
        select(QuestInstance)
        .where(QuestInstance.quest_id == quest.id)
        .order_by(QuestInstance.quest_date.desc(), QuestInstance.id.desc())
    )


def add_progress(
    db: Session,
    player: Player,
    quest: Quest,
    instance: QuestInstance,
    amount: int,
    settings: Settings,
) -> tuple[QuestInstance, bool]:
    """Record progress, completing the instance if it reaches its target.

    Returns the instance and whether this call completed it.
    """
    if amount == 0:
        raise ValidationError("Progress amount must not be zero.")
    if instance.status is not QuestStatus.ACTIVE:
        raise ValidationError(
            f"Quest instance is already {instance.status.value}; it cannot take progress."
        )

    instance.progress = max(0, instance.progress + amount)

    log_event(
        db,
        player,
        EventType.QUEST_PROGRESS,
        f"{quest.title}: {instance.progress}/{instance.target_count}",
        {
            "quest_id": quest.id,
            "instance_id": instance.id,
            "progress": instance.progress,
            "target_count": instance.target_count,
        },
    )

    if instance.is_cleared:
        complete_instance(db, player, quest, instance, settings)
        return instance, True

    return instance, False


def complete_instance(
    db: Session,
    player: Player,
    quest: Quest,
    instance: QuestInstance,
    settings: Settings,
) -> QuestInstance:
    """Clear an instance and pay out its rewards."""
    if instance.status is QuestStatus.COMPLETED:
        raise ValidationError("Quest instance is already completed.")
    if instance.status is QuestStatus.FAILED:
        raise ValidationError("Quest instance has already failed; it cannot be cleared.")

    instance.status = QuestStatus.COMPLETED
    instance.progress = max(instance.progress, instance.target_count)
    instance.completed_at = clock.utcnow()

    if quest.stat_reward is not None and quest.stat_reward_amount:
        player.add_stat(quest.stat_reward, quest.stat_reward_amount)

    result = award_exp(
        db, player, quest.exp_reward, settings, source=f"quest:{quest.id}"
    )

    log_event(
        db,
        player,
        EventType.QUEST_COMPLETED,
        f"Quest complete: {quest.title} (+{quest.exp_reward} EXP)",
        {
            "quest_id": quest.id,
            "instance_id": instance.id,
            "exp_gained": quest.exp_reward,
            "stat_reward": quest.stat_reward.value if quest.stat_reward else None,
            "stat_reward_amount": quest.stat_reward_amount,
            "leveled_up": result.leveled_up,
        },
    )

    # Clearing a one-shot quest retires it; a daily respawns tomorrow.
    if quest.quest_type is QuestType.NORMAL:
        quest.is_active = False

    return instance
