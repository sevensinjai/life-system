"""Quest lifecycle: authoring, progress, completion."""

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
    ScheduleKind,
    StatName,
)
from app.services import clock, scheduling, skills
from app.services.progression import award_exp, log_event
from app.services.scheduling import Period, Schedule, ScheduleError
from app.services.skills import SkillAward


def default_exp_for(difficulty: QuestDifficulty) -> int:
    """The EXP a quest of this difficulty is worth unless the author overrides it."""
    return DIFFICULTY_EXP[difficulty]


def schedule_of(quest: Quest) -> Schedule:
    """Read a quest's stored columns back into a Schedule value."""
    return Schedule(
        kind=quest.schedule,
        days=tuple(quest.schedule_days or ()),
        interval_days=quest.schedule_interval_days,
        anchor=quest.schedule_anchor,
        week_start=quest.week_start,
    )


def build_schedule(
    kind: ScheduleKind,
    *,
    days=None,
    interval_days: int | None = None,
    anchor: date | None = None,
    week_start: int = 0,
) -> Schedule:
    """Validate authored schedule input, surfacing failures as 422s."""
    try:
        return Schedule(
            kind=kind,
            days=scheduling.normalize_days(days or ()),
            interval_days=interval_days,
            anchor=anchor,
            week_start=week_start,
        )
    except ScheduleError as exc:
        raise ValidationError(str(exc)) from exc


def resolve_skill_reward(
    db: Session,
    player: Player,
    skill_id: int | None,
    skill_exp_reward: int | None,
    exp_reward: int,
) -> int:
    """Validate a quest's skill link and settle how much EXP it pays the skill.

    Naming a skill without an amount means "worth the same to the skill as it
    is to me", which is the reading that needs no extra thought when authoring.
    Verifying ownership here is what stops a quest from pointing at someone
    else's skill.
    """
    if skill_id is None:
        return 0

    skills.get_skill(db, player, skill_id)  # 404s if it is not the player's
    if skill_exp_reward is not None:
        if skill_exp_reward < 0:
            raise ValidationError("skill_exp_reward must be non-negative.")
        return skill_exp_reward
    return exp_reward


def create_quest(
    db: Session,
    player: Player,
    *,
    title: str,
    description: str | None = None,
    schedule: Schedule | None = None,
    difficulty: QuestDifficulty = QuestDifficulty.E,
    target_count: int = 1,
    unit: str | None = None,
    exp_reward: int | None = None,
    stat_reward: StatName | None = None,
    stat_reward_amount: int = 0,
    skill_id: int | None = None,
    skill_exp_reward: int | None = None,
    today: date | None = None,
) -> Quest:
    """Author a quest and open its first period.

    A quest whose schedule does not fall on today is created without an open
    instance; the reset opens one when its first period arrives.
    """
    if target_count < 1:
        raise ValidationError("target_count must be at least 1.")
    if stat_reward_amount < 0:
        raise ValidationError("stat_reward_amount must be non-negative.")

    exp_reward = exp_reward if exp_reward is not None else default_exp_for(difficulty)
    skill_exp_reward = resolve_skill_reward(
        db, player, skill_id, skill_exp_reward, exp_reward
    )

    today = today or clock.local_date(player.timezone)
    schedule = schedule or Schedule(kind=ScheduleKind.ONCE, anchor=today)

    # Anchoring at creation makes an interval quest count from the day it was
    # authored, which is what the author means by "every 3 days".
    if schedule.anchor is None:
        schedule = Schedule(
            kind=schedule.kind,
            days=schedule.days,
            interval_days=schedule.interval_days,
            anchor=today,
            week_start=schedule.week_start,
        )

    quest = Quest(
        player_id=player.id,
        title=title,
        description=description,
        schedule=schedule.kind,
        schedule_days=list(schedule.days) or None,
        schedule_interval_days=schedule.interval_days,
        schedule_anchor=schedule.anchor,
        week_start=schedule.week_start,
        difficulty=difficulty,
        target_count=target_count,
        unit=unit,
        exp_reward=exp_reward,
        stat_reward=stat_reward,
        stat_reward_amount=stat_reward_amount,
        skill_id=skill_id,
        skill_exp_reward=skill_exp_reward,
    )
    db.add(quest)
    db.flush()  # assign quest.id before building its instance

    period = scheduling.current_period(schedule, today)
    if period is not None:
        get_or_create_instance(db, quest, period)

    log_event(
        db,
        player,
        EventType.QUEST_CREATED,
        f"New quest accepted: {quest.title}",
        {
            "quest_id": quest.id,
            "schedule": quest.schedule.value,
            "schedule_label": scheduling.describe(schedule),
        },
    )
    return quest


def get_or_create_instance(
    db: Session, quest: Quest, period: Period
) -> QuestInstance:
    """Fetch the quest's instance for a period, creating it if absent.

    Idempotent, which is what lets the reset run repeatedly without spawning
    duplicates.
    """
    existing = db.scalar(
        select(QuestInstance).where(
            QuestInstance.quest_id == quest.id,
            QuestInstance.period_start == period.start,
        )
    )
    if existing is not None:
        return existing

    instance = QuestInstance(
        quest_id=quest.id,
        player_id=quest.player_id,
        period_start=period.start,
        period_end=period.end,
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
    schedule: ScheduleKind | None = None,
    recurring_only: bool = False,
    include_archived: bool = False,
) -> list[Quest]:
    """List the player's authored quests, newest first."""
    stmt = select(Quest).where(Quest.player_id == player.id)
    if schedule is not None:
        stmt = stmt.where(Quest.schedule == schedule)
    if recurring_only:
        stmt = stmt.where(Quest.schedule != ScheduleKind.ONCE)
    if not include_archived:
        stmt = stmt.where(Quest.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Quest.created_at.desc(), Quest.id.desc())))


def current_instance(
    db: Session, quest: Quest, today: date | None = None, player: Player | None = None
) -> QuestInstance | None:
    """The instance the player would act on right now.

    That is the instance whose period covers today. A quest that is not due
    today — a Mon/Wed/Fri quest on a Tuesday — has none.
    """
    today = today or clock.local_date(player.timezone if player else "UTC")

    return db.scalar(
        select(QuestInstance)
        .where(
            QuestInstance.quest_id == quest.id,
            QuestInstance.period_start <= today,
            (QuestInstance.period_end.is_(None))
            | (QuestInstance.period_end >= today),
        )
        .order_by(QuestInstance.period_start.desc(), QuestInstance.id.desc())
    )


def next_due_date(quest: Quest, today: date) -> date | None:
    """When this quest next opens a period, for the client to display.

    Always the *next* period, never the open one: a client showing "next up"
    wants tomorrow's date while today's instance is still in hand. None for a
    one-time quest, which never comes around again.
    """
    schedule = schedule_of(quest)
    if not scheduling.is_recurring(schedule):
        return None
    return scheduling.next_occurrence(schedule, today)


def add_progress(
    db: Session,
    player: Player,
    quest: Quest,
    instance: QuestInstance,
    amount: int,
    settings: Settings,
) -> tuple[QuestInstance, bool, list[SkillAward]]:
    """Record progress, completing the instance if it reaches its target.

    Returns the instance, whether this call completed it, and any skill EXP
    the completion paid out.
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
        _, awards = complete_instance(db, player, quest, instance, settings)
        return instance, True, awards

    return instance, False, []


def complete_instance(
    db: Session,
    player: Player,
    quest: Quest,
    instance: QuestInstance,
    settings: Settings,
) -> tuple[QuestInstance, list[SkillAward]]:
    """Clear an instance and pay out its rewards.

    Returns the instance and the skill awards, which are what the client
    animates alongside the player's own level-up.
    """
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
    skill_awards = skills.award_for_quest(db, player, quest, settings)

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
            "skill_id": quest.skill_id,
            "skill_exp_gained": skill_awards[0].exp_gained if skill_awards else 0,
        },
    )

    # Clearing a one-time quest retires it; a recurring one comes back.
    if quest.schedule is ScheduleKind.ONCE:
        quest.is_active = False

    return instance, skill_awards
