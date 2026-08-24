"""The pantheon: who is watching, and what they make of you."""

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.deps import CurrentPlayer, DbDep
from app.models import Constellation, Player
from app.schemas.constellation import ConstellationResponse, StandingBlock
from app.services import constellations, story

router = APIRouter(prefix="/constellations", tags=["constellations"])


def _with_standing(
    db: Session, player: Player, constellation: Constellation
) -> ConstellationResponse:
    """One constellation, answered from this player's side of it."""
    favor = constellations.get_favor(db, player, constellation)

    return ConstellationResponse(
        code=constellation.code,
        name=constellation.name,
        epithet=constellation.epithet,
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
    )


@router.get(
    "",
    response_model=list[ConstellationResponse],
    summary="Who is watching",
)
def index(player: CurrentPlayer, db: DbDep) -> list[ConstellationResponse]:
    """The whole pantheon, each with where you stand in it.

    A read, and a safe one: a constellation you have never heard from comes
    back as a stranger with an empty record rather than being created on the
    spot. Opting out of side quests does not hide them — you can look up at
    who is there without agreeing to be interrupted by them.
    """
    return [
        _with_standing(db, player, constellation)
        for constellation in constellations.list_constellations(db)
    ]


@router.get(
    "/{code}",
    response_model=ConstellationResponse,
    summary="One constellation",
)
def show(code: str, player: CurrentPlayer, db: DbDep) -> ConstellationResponse:
    """One of them, by its stable code, retired ones included."""
    return _with_standing(db, player, constellations.get_by_code(db, code))
