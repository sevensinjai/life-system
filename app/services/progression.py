"""Player progression: awarding EXP, levelling up, penalties, stat allocation."""

from typing import Any

from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import ValidationError
from app.models import EventType, Penalty, Player, QuestInstance, StatName, SystemEvent
from app.services import leveling


def log_event(
    db: Session,
    player: Player,
    event_type: EventType,
    message: str,
    payload: dict[str, Any] | None = None,
) -> SystemEvent:
    """Append an entry to the player's system log."""
    event = SystemEvent(
        player_id=player.id,
        event_type=event_type,
        message=message,
        payload=payload or {},
    )
    db.add(event)
    return event


def award_exp(
    db: Session,
    player: Player,
    amount: int,
    settings: Settings,
    *,
    source: str = "",
) -> leveling.ExpResult:
    """Grant EXP, applying any level-ups and the stat points they carry."""
    if amount < 0:
        raise ValidationError("EXP award must be non-negative.")

    result = leveling.gain_exp(
        player.level,
        player.exp,
        amount,
        base=settings.exp_curve_base,
        exponent=settings.exp_curve_exponent,
    )

    player.level = result.level
    player.exp = result.exp
    player.total_exp_earned += amount

    if result.leveled_up:
        gained_points = result.levels_gained * settings.stat_points_per_level
        player.stat_points += gained_points
        log_event(
            db,
            player,
            EventType.LEVEL_UP,
            f"Level up! You are now Level {player.level}.",
            {
                "new_level": player.level,
                "levels_gained": result.levels_gained,
                "stat_points_gained": gained_points,
                "source": source,
            },
        )

    return result


def apply_exp_penalty(
    db: Session,
    player: Player,
    amount: int,
    *,
    reason: str,
    instance: QuestInstance | None = None,
) -> Penalty:
    """Dock EXP and record why.

    The amount recorded is what was actually lost, which can be less than
    `amount` when the player had too little EXP to take the full hit.
    """
    if amount < 0:
        raise ValidationError("Penalty amount must be non-negative.")

    before = player.exp
    result = leveling.lose_exp(player.level, player.exp, amount)
    player.exp = result.exp
    actually_lost = before - result.exp

    penalty = Penalty(
        player_id=player.id,
        quest_instance_id=instance.id if instance else None,
        reason=reason,
        exp_lost=actually_lost,
    )
    db.add(penalty)

    log_event(
        db,
        player,
        EventType.PENALTY_APPLIED,
        f"Penalty incurred: {reason} (-{actually_lost} EXP)",
        {"exp_lost": actually_lost, "reason": reason},
    )

    return penalty


def allocate_stats(
    db: Session, player: Player, allocations: dict[StatName, int]
) -> Player:
    """Spend unallocated stat points.

    Rejected wholesale if the player cannot afford the total, so a partial
    allocation can never be applied.
    """
    cleaned = {stat: n for stat, n in allocations.items() if n}

    if any(n < 0 for n in cleaned.values()):
        raise ValidationError("Stat allocations must be non-negative.")

    total = sum(cleaned.values())
    if total == 0:
        raise ValidationError("Allocate at least one stat point.")
    if total > player.stat_points:
        raise ValidationError(
            f"Not enough stat points: tried to spend {total}, "
            f"but only {player.stat_points} available."
        )

    for stat, points in cleaned.items():
        player.add_stat(stat, points)
    player.stat_points -= total

    log_event(
        db,
        player,
        EventType.STATS_ALLOCATED,
        f"Allocated {total} stat point{'s' if total != 1 else ''}.",
        {"allocations": {stat.value: n for stat, n in cleaned.items()}},
    )

    return player
