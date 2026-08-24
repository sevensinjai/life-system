"""The pantheon: who is watching, and what they make of you."""

from fastapi import APIRouter, Query, status
from sqlalchemy.orm import Session

from app.deps import CurrentPlayer, DbDep, SettingsDep
from app.models import Constellation, FriendshipStatus, MythTradition, Player
from app.schemas.constellation import (
    ConstellationResponse,
    FriendshipBlock,
    FriendshipRequestBody,
    FriendshipRequestResponse,
    StandingBlock,
)
from app.services import clock, constellations, friendship, story

router = APIRouter(prefix="/constellations", tags=["constellations"])


def _friendship_block(
    db: Session, player: Player, constellation: Constellation
) -> FriendshipBlock:
    """Where the player stands on being one of this constellation's friends."""
    favor = constellations.get_favor(db, player, constellation)
    now = clock.utcnow()
    allowed, blocked_by = friendship.may_ask(db, player, constellation, now)
    latest = friendship.latest_request(db, player, constellation)

    return FriendshipBlock(
        is_friend=favor.is_friend,
        befriended_at=favor.befriended_at,
        may_ask=allowed,
        blocked_by=blocked_by,
        retry_after=friendship.retry_at(db, player, constellation),
        request_status=latest.status if latest else None,
        challenge_offer_id=(
            latest.challenge_offer_id
            if latest and latest.status is FriendshipStatus.CHALLENGED
            else None
        ),
    )


def _with_standing(
    db: Session, player: Player, constellation: Constellation
) -> ConstellationResponse:
    """One constellation, answered from this player's side of it."""
    favor = constellations.get_favor(db, player, constellation)

    return ConstellationResponse(
        code=constellation.code,
        tradition=constellation.tradition,
        code_name=constellation.code_name,
        code_name_zh_hant=constellation.code_name_zh_hant,
        real_name=constellation.real_name,
        real_name_zh_hant=constellation.real_name_zh_hant,
        epithet=constellation.epithet,
        epithet_zh_hant=constellation.epithet_zh_hant,
        description=constellation.description,
        domain=constellation.domain,
        standing=StandingBlock(
            standing=story.standing_for(favor.favor),
            favor=favor.favor,
            offers_received=favor.offers_received,
            completed=favor.completed,
            declined=favor.declined,
            expired=favor.expired,
            failed=favor.failed,
            first_seen_at=favor.first_seen_at,
            last_seen_at=favor.last_seen_at,
        ),
        friendship=_friendship_block(db, player, constellation),
    )


@router.get(
    "",
    response_model=list[ConstellationResponse],
    summary="Who is watching",
)
def index(
    player: CurrentPlayer,
    db: DbDep,
    tradition: MythTradition | None = Query(
        default=None, description="Narrow to one body of myth."
    ),
) -> list[ConstellationResponse]:
    """The whole pantheon, each with where you stand in it.

    A read, and a safe one: a constellation you have never heard from comes
    back as a stranger with an empty record rather than being created on the
    spot. Opting out of side quests does not hide them — you can look up at
    who is there without agreeing to be interrupted by them.

    Each carries a `friendship` block, because this is the screen you decide
    from: whether it issues to you, whether you may ask it to, and when you
    may ask again if you may not.

    Twenty-six of them is a long list, so `?tradition=` narrows it to one
    body of myth.
    """
    return [
        _with_standing(db, player, constellation)
        for constellation in constellations.list_constellations(db, tradition=tradition)
    ]


@router.get(
    "/{code}",
    response_model=ConstellationResponse,
    summary="One constellation",
)
def show(code: str, player: CurrentPlayer, db: DbDep) -> ConstellationResponse:
    """One of them, by its stable code, retired ones included."""
    return _with_standing(db, player, constellations.get_by_code(db, code))


@router.post(
    "/{code}/friendship",
    response_model=FriendshipRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ask a constellation to befriend you",
)
def request_friendship(
    code: str,
    payload: FriendshipRequestBody,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> FriendshipRequestResponse:
    """Put your case to a constellation, and get its answer at once.

    A constellation issues trials to its friends and to nobody else, so this
    is the way in. It may decline to hear you — in which case `retry_after`
    says when you may ask again — or it may set you a **trial of admission**,
    which arrives as an ordinary side quest. Clear that and you are friends;
    fail, decline, or ignore it and the request closes with the same wait.

    Both answers are answers, not errors. The 422 is for asking when you may
    not: already friends, a trial still open, or still inside the wait.
    """
    constellation = constellations.get_by_code(db, code)
    request = friendship.request_friendship(
        db, player, constellation, settings, message=payload.message
    )
    db.commit()

    return FriendshipRequestResponse(
        status=request.status,
        constellation=constellation.code,
        line=_last_line(db, player),
        retry_after=friendship.retry_at(db, player, constellation),
        challenge_offer_id=request.challenge_offer_id,
    )


def _last_line(db: Session, player: Player) -> str | None:
    """What the constellation just said, read back off the log it wrote to.

    Read from the event rather than re-resolved, so the response and the
    notification feed can never disagree about what was said.
    """
    from sqlalchemy import select

    from app.models import SystemEvent

    event = db.scalar(
        select(SystemEvent)
        .where(SystemEvent.player_id == player.id)
        .order_by(SystemEvent.id.desc())
    )
    return (event.payload or {}).get("line") if event else None


@router.delete(
    "/{code}/friendship",
    response_model=ConstellationResponse,
    summary="End a friendship",
)
def end_friendship(
    code: str, player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> ConstellationResponse:
    """Walk away from a constellation.

    Its trials stop reaching you. Your standing with it is left exactly where
    it stood — the history happened — but asking to come back waits out the
    same period a refusal does, so this is not a switch to flip twice a day.
    Anything you already accepted stays yours to finish.
    """
    constellation = constellations.get_by_code(db, code)
    friendship.end_friendship(db, player, constellation, settings)
    db.commit()
    return _with_standing(db, player, constellation)
