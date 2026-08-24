"""The reset: lapse periods that closed unfinished, open the ones due now.

This is the loop that gives the System its teeth. It is schedule-agnostic —
a period that ended before today lapses, whether that period was one day, one
week, or an author's custom interval. One-time quests have no period end, so
they can never lapse.
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
    ScheduleKind,
)
from app.services import clock, scheduling, side_quests
from app.services.progression import apply_exp_penalty, log_event
from app.services.quests import get_or_create_instance, schedule_of


@dataclass
class DailyResetResult:
    """What one reset actually did."""

    reset_date: date
    failed_quest_ids: list[int] = field(default_factory=list)
    spawned_quest_ids: list[int] = field(default_factory=list)
    # Side quests settled on the way past: ones never answered, and ones
    # accepted and then left unfinished.
    expired_side_quest_ids: list[int] = field(default_factory=list)
    failed_side_quest_ids: list[int] = field(default_factory=list)
    # Every EXP loss this reset caused, quests and side quests together.
    total_exp_lost: int = 0

    @property
    def failed_count(self) -> int:
        return len(self.failed_quest_ids)

    @property
    def spawned_count(self) -> int:
        return len(self.spawned_quest_ids)

    @property
    def side_quests_expired(self) -> int:
        return len(self.expired_side_quest_ids)

    @property
    def side_quests_failed(self) -> int:
        return len(self.failed_side_quest_ids)

    @property
    def did_anything(self) -> bool:
        return bool(
            self.failed_quest_ids
            or self.spawned_quest_ids
            or self.expired_side_quest_ids
            or self.failed_side_quest_ids
        )


def run_daily_reset(
    db: Session,
    player: Player,
    settings: Settings,
    *,
    now=None,
) -> DailyResetResult:
    """Lapse closed periods and open the ones due today.

    Idempotent: calling it repeatedly within the same local day is a no-op,
    because lapsed instances leave ACTIVE status and instance creation is
    unique per (quest, period_start).

    Side quests ride along here rather than getting their own rollover call.
    Their windows are UTC instants, not local days, so the sweep is a matter
    of "settle anything whose deadline has passed" — which this is already the
    place for, and which the app already calls on launch.
    """
    today = clock.local_date(player.timezone, now)
    result = DailyResetResult(reset_date=today)

    _expire_lapsed(db, player, settings, today, result)
    _open_due_periods(db, player, today, result)
    _settle_side_quests(db, player, settings, result, now)

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
                "side_quests_expired": result.side_quests_expired,
                "side_quests_failed": result.side_quests_failed,
                "exp_lost": result.total_exp_lost,
            },
        )

    return result


def _expire_lapsed(
    db: Session,
    player: Player,
    settings: Settings,
    today: date,
    result: DailyResetResult,
) -> None:
    """Fail every instance whose period closed before today, and penalize it."""
    lapsed = db.scalars(
        select(QuestInstance)
        .where(
            QuestInstance.player_id == player.id,
            QuestInstance.status == QuestStatus.ACTIVE,
            QuestInstance.period_end.is_not(None),
            QuestInstance.period_end < today,
        )
        .order_by(QuestInstance.period_start)
    ).all()

    for instance in lapsed:
        quest = db.get(Quest, instance.quest_id)
        if quest is None:
            continue

        instance.status = QuestStatus.FAILED
        result.failed_quest_ids.append(quest.id)

        log_event(
            db,
            player,
            EventType.QUEST_FAILED,
            f"Quest failed: {quest.title} "
            f"({instance.progress}/{instance.target_count})",
            {
                "quest_id": quest.id,
                "instance_id": instance.id,
                "period_start": instance.period_start.isoformat(),
                "period_end": instance.period_end.isoformat()
                if instance.period_end
                else None,
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
                reason=f"Failed quest: {quest.title}",
                instance=instance,
            )
            result.total_exp_lost += penalty.exp_lost


def _open_due_periods(
    db: Session, player: Player, today: date, result: DailyResetResult
) -> None:
    """Ensure every recurring quest due today has an open instance."""
    recurring = db.scalars(
        select(Quest).where(
            Quest.player_id == player.id,
            Quest.schedule != ScheduleKind.ONCE,
            Quest.is_active.is_(True),
        )
    ).all()

    for quest in recurring:
        period = scheduling.current_period(schedule_of(quest), today)
        if period is None:
            continue  # not due today, e.g. a Mon/Wed/Fri quest on a Tuesday

        existing = db.scalar(
            select(QuestInstance).where(
                QuestInstance.quest_id == quest.id,
                QuestInstance.period_start == period.start,
            )
        )
        if existing is None:
            get_or_create_instance(db, quest, period)
            result.spawned_quest_ids.append(quest.id)


def _settle_side_quests(
    db: Session,
    player: Player,
    settings: Settings,
    result: DailyResetResult,
    now,
) -> None:
    """Close out side quest offers whose windows have passed."""
    swept = side_quests.sweep_offers(db, player, settings, now=now)
    result.expired_side_quest_ids.extend(swept.expired_offer_ids)
    result.failed_side_quest_ids.extend(swept.failed_offer_ids)
    result.total_exp_lost += swept.total_exp_lost


def _reset_message(result: DailyResetResult) -> str:
    parts = []
    if result.failed_count:
        parts.append(
            f"{result.failed_count} quest"
            f"{'s' if result.failed_count != 1 else ''} failed"
        )
    if result.spawned_count:
        parts.append(f"{result.spawned_count} quest(s) issued")
    if result.side_quests_failed:
        parts.append(f"{result.side_quests_failed} side quest(s) failed")
    if result.side_quests_expired:
        parts.append(f"{result.side_quests_expired} side quest(s) expired")

    # One EXP figure at the end, covering quests and side quests together.
    lost = f" (-{result.total_exp_lost} EXP)" if result.total_exp_lost else ""
    return "Reset: " + ", ".join(parts) + lost + "."


def run_daily_reset_for_all(
    db: Session, settings: Settings, *, now=None
) -> dict[int, DailyResetResult]:
    """Run the reset for every player. Intended for a scheduled job."""
    results: dict[int, DailyResetResult] = {}
    for player in db.scalars(select(Player)).all():
        results[player.id] = run_daily_reset(db, player, settings, now=now)
    db.commit()
    return results
