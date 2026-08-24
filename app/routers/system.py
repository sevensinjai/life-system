"""The System itself: daily rollover, the event log, and penalty history."""

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.deps import CurrentPlayer, DbDep, SettingsDep
from app.models import EventType, Penalty, SystemEvent
from app.schemas.event import DailyResetResponse, PenaltyResponse, SystemEventResponse
from app.services.daily import run_daily_reset

router = APIRouter(prefix="/system", tags=["system"])


@router.post(
    "/daily-reset",
    response_model=DailyResetResponse,
    summary="Roll the day over",
)
def daily_reset(
    player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> DailyResetResponse:
    """Fail any daily quest left unfinished on a past date, then issue today's.

    Also settles side quests whose windows have closed: unanswered ones expire
    for free, accepted ones that fell short fail and pay their penalty.

    Safe to call on every app launch: it is idempotent within a local day, so
    repeat calls neither double-penalize nor duplicate quests.
    """
    result = run_daily_reset(db, player, settings)
    db.commit()

    return DailyResetResponse(
        reset_date=result.reset_date,
        failed_count=result.failed_count,
        spawned_count=result.spawned_count,
        side_quests_expired=result.side_quests_expired,
        side_quests_failed=result.side_quests_failed,
        total_exp_lost=result.total_exp_lost,
    )


@router.get(
    "/events",
    response_model=list[SystemEventResponse],
    summary="System log",
)
def events(
    player: CurrentPlayer,
    db: DbDep,
    event_type: EventType | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[SystemEvent]:
    """The player's notification feed, newest first."""
    stmt = select(SystemEvent).where(SystemEvent.player_id == player.id)
    if event_type is not None:
        stmt = stmt.where(SystemEvent.event_type == event_type)
    stmt = stmt.order_by(SystemEvent.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt))


@router.get(
    "/penalties",
    response_model=list[PenaltyResponse],
    summary="Penalty history",
)
def penalties(
    player: CurrentPlayer,
    db: DbDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Penalty]:
    """Every EXP loss on record, newest first."""
    stmt = (
        select(Penalty)
        .where(Penalty.player_id == player.id)
        .order_by(Penalty.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt))
