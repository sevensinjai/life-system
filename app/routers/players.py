"""The status window and stat allocation."""

from fastapi import APIRouter

from app.deps import CurrentPlayer, DbDep, SettingsDep
from app.errors import ValidationError
from app.schemas.player import AllocateStatsRequest, PlayerStatus, UpdatePlayerRequest
from app.services.clock import is_valid_timezone
from app.services.progression import allocate_stats
from app.services.status import build_player_status

router = APIRouter(prefix="/players", tags=["player"])


@router.get("/me", response_model=PlayerStatus, summary="Status window")
def get_status(
    player: CurrentPlayer, settings: SettingsDep
) -> PlayerStatus:
    """Level, EXP, and stats — everything the main screen renders.

    Read-only. Daily quests are rolled over by POST /system/daily-reset, not
    here, so this endpoint never changes state.
    """
    return build_player_status(player, settings)


@router.patch("/me", response_model=PlayerStatus, summary="Update name or timezone")
def update_player(
    payload: UpdatePlayerRequest,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> PlayerStatus:
    """Change the player's name or timezone.

    Moving timezone shifts when daily quests roll over; it does not retroactively
    re-date instances that already exist.
    """
    if payload.name is not None:
        player.name = payload.name

    if payload.timezone is not None:
        if not is_valid_timezone(payload.timezone):
            raise ValidationError(
                f"{payload.timezone!r} is not a known IANA timezone "
                "(for example: 'Asia/Seoul')."
            )
        player.timezone = payload.timezone

    db.commit()
    return build_player_status(player, settings)


@router.post(
    "/me/allocate", response_model=PlayerStatus, summary="Spend stat points"
)
def allocate(
    payload: AllocateStatsRequest,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> PlayerStatus:
    """Spend unallocated stat points. All-or-nothing if you cannot afford it."""
    allocate_stats(db, player, payload.as_allocations())
    db.commit()
    return build_player_status(player, settings)
