"""The daily reset: expire yesterday's unfinished dailies, spawn today's.

This is the loop that gives the System its teeth. It runs when the player's
local date has moved past an open daily instance — whether triggered by a
scheduled job or lazily on the player's next request.
"""

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import (
    EventType,
    Player,
    Quest,
    QuestInstance,
    QuestStatus,
    QuestType,
)
from app.services import clock
from app.services.progression import apply_exp_penalty, log_event
from app.services.quests import get_or_create_instance


@dataclass
class DailyResetResult:
    """What one reset actually did."""

    reset_date: date
    failed_quest_ids: list[int] = field(default_factory=list)
    spawned_quest_ids: list[int] = field(default_factory=list)
    total_exp_lost: int = 0

    @property
    def failed_count(self) -> int:
        return len(self.failed_quest_ids)

    @property
    def spawned_count(self) -> int:
        return len(self.spawned_quest_ids)

    @property
    def did_anything(self) -> bool:
        return bool(self.failed_quest_ids or self.spawned_quest_ids)


def run_daily_reset(
    db: Session,
    player: Player,
    settings: Settings,
    *,
    now=None,
) -> DailyResetResult:
    """Expire overdue daily instances and open today's.

    Idempotent: calling it repeatedly within the same local day is a no-op,
    because expired instances leave ACTIVE status and instance creation is
    unique per (quest, date).
    """
    today = clock.local_date(player.timezone, now)
    result = DailyResetResult(reset_date=today)

    _expire_overdue(db, player, settings, today, result)
    _spawn_today(db, player, today, result)

    if result.did_anything:
        log_event(
            db,
            player,
            EventType.DAILY_RESET,
            _reset_message(result),
            {
                "date": today.isoformat(),
                "failed": result.failed_count,
                "spawned": result.spawned_count,
                "exp_lost": result.total_exp_lost,
            },
        )

    return result


def _expire_overdue(
    db: Session,
    player: Player,
    settings: Settings,
    today: date,
    result: DailyResetResult,
) -> None:
    """Fail every daily instance left active on a past date, and penalize it."""
    overdue = db.scalars(
        select(QuestInstance)
        .join(Quest, Quest.id == QuestInstance.quest_id)
        .where(
            QuestInstance.player_id == player.id,
            QuestInstance.status == QuestStatus.ACTIVE,
            QuestInstance.quest_date < today,
            Quest.quest_type == QuestType.DAILY,
        )
        .order_by(QuestInstance.quest_date)
    ).all()

    for instance in overdue:
        quest = db.get(Quest, instance.quest_id)
        if quest is None:
            continue

        instance.status = QuestStatus.FAILED
        result.failed_quest_ids.append(quest.id)

        log_event(
            db,
            player,
            EventType.QUEST_FAILED,
            f"Daily quest failed: {quest.title} "
            f"({instance.progress}/{instance.target_count})",
            {
                "quest_id": quest.id,
                "instance_id": instance.id,
                "quest_date": instance.quest_date.isoformat(),
                "progress": instance.progress,
                "target_count": instance.target_count,
            },
        )

        penalty_amount = round(quest.exp_reward * settings.penalty_exp_multiplier)
        if penalty_amount > 0:
            penalty = apply_exp_penalty(
                db,
                player,
                penalty_amount,
                reason=f"Failed daily quest: {quest.title}",
                instance=instance,
            )
            result.total_exp_lost += penalty.exp_lost


def _spawn_today(
    db: Session, player: Player, today: date, result: DailyResetResult
) -> None:
    """Ensure every active daily quest has an instance for today."""
    dailies = db.scalars(
        select(Quest).where(
            Quest.player_id == player.id,
            Quest.quest_type == QuestType.DAILY,
            Quest.is_active.is_(True),
        )
    ).all()

    for quest in dailies:
        existing = db.scalar(
            select(QuestInstance).where(
                QuestInstance.quest_id == quest.id,
                QuestInstance.quest_date == today,
            )
        )
        if existing is None:
            get_or_create_instance(db, quest, today)
            result.spawned_quest_ids.append(quest.id)


def _reset_message(result: DailyResetResult) -> str:
    parts = []
    if result.failed_count:
        parts.append(
            f"{result.failed_count} daily quest"
            f"{'s' if result.failed_count != 1 else ''} failed "
            f"(-{result.total_exp_lost} EXP)"
        )
    if result.spawned_count:
        parts.append(f"{result.spawned_count} daily quest(s) issued")
    return "Daily reset: " + ", ".join(parts) + "."


def run_daily_reset_for_all(
    db: Session, settings: Settings, *, now=None
) -> dict[int, DailyResetResult]:
    """Run the reset for every player. Intended for a scheduled job."""
    results: dict[int, DailyResetResult] = {}
    for player in db.scalars(select(Player)).all():
        results[player.id] = run_daily_reset(db, player, settings, now=now)
    db.commit()
    return results
