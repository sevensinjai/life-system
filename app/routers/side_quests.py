"""Side quests: opting in to the System's broadcasts, and answering them."""

from fastapi import APIRouter, Query, status
from sqlalchemy.orm import Session

from app.deps import CurrentPlayer, DbDep, SettingsDep
from app.models import Player, SideQuestOffer, SideQuestOfferStatus
from app.schemas.side_quest import (
    SideQuestOfferResponse,
    SideQuestPreferenceResponse,
    SideQuestPreferenceUpdate,
    SideQuestProgressRequest,
    SideQuestProgressResponse,
)
from app.services import clock, side_quests
from app.services.side_quests import UNSET

router = APIRouter(prefix="/side-quests", tags=["side quests"])


def _preference_response(db: Session, player: Player) -> SideQuestPreferenceResponse:
    """The player's settings plus the counts that make them concrete."""
    preference = side_quests.get_preference(db, player)
    live = side_quests.list_offers(db, player, live_only=True)

    return SideQuestPreferenceResponse(
        is_opted_in=preference.is_opted_in,
        frequency=preference.frequency,
        max_difficulty=preference.max_difficulty,
        auto_accept=preference.auto_accept,
        offers_per_week=side_quests.offers_per_week(preference),
        offers_this_week=side_quests.offers_in_window(db, player, clock.utcnow()),
        open_offers=len(live),
        opted_in_at=preference.opted_in_at,
        opted_out_at=preference.opted_out_at,
    )


@router.get(
    "/preferences",
    response_model=SideQuestPreferenceResponse,
    summary="Your side quest settings",
)
def get_preferences(player: CurrentPlayer, db: DbDep) -> SideQuestPreferenceResponse:
    """Whether you are listening for side quests, and on what terms.

    A player who has never answered reads back as opted out — the System does
    not enrol anybody quietly.
    """
    return _preference_response(db, player)


@router.patch(
    "/preferences",
    response_model=SideQuestPreferenceResponse,
    summary="Opt in or out of side quests",
)
def update_preferences(
    payload: SideQuestPreferenceUpdate, player: CurrentPlayer, db: DbDep
) -> SideQuestPreferenceResponse:
    """Turn side quests on or off, and set how often they may reach you.

    Opting in takes effect immediately: any broadcast still open that you are
    eligible for is offered to you on the spot, up to your frequency cap,
    rather than making you wait for the next one.

    Opting out stops new offers. Anything you already accepted stays yours to
    finish — the System does not retract a quest you took up.
    """
    fields = payload.model_dump(exclude_unset=True)

    preference = side_quests.set_preference(
        db,
        player,
        is_opted_in=fields.get("is_opted_in"),
        frequency=fields.get("frequency"),
        max_difficulty=fields.get("max_difficulty", UNSET),
        auto_accept=fields.get("auto_accept"),
    )

    if preference.is_opted_in:
        side_quests.catch_up(db, player)

    db.commit()
    return _preference_response(db, player)


@router.get(
    "",
    response_model=list[SideQuestOfferResponse],
    summary="Side quests you have been offered",
)
def index(
    player: CurrentPlayer,
    db: DbDep,
    status_filter: SideQuestOfferStatus | None = Query(default=None, alias="status"),
    live_only: bool = Query(
        default=False, description="Only ones still awaiting you or in progress."
    ),
) -> list[SideQuestOffer]:
    """Your side quest history, newest first."""
    return side_quests.list_offers(
        db, player, status=status_filter, live_only=live_only
    )


@router.get(
    "/{offer_id}",
    response_model=SideQuestOfferResponse,
    summary="Fetch one side quest offer",
)
def show(offer_id: int, player: CurrentPlayer, db: DbDep) -> SideQuestOffer:
    return side_quests.get_offer(db, player, offer_id)


@router.post(
    "/{offer_id}/accept",
    response_model=SideQuestOfferResponse,
    summary="Accept a side quest",
)
def accept(offer_id: int, player: CurrentPlayer, db: DbDep) -> SideQuestOffer:
    """Take the quest up.

    This is the point where it can start to cost you: an accepted side quest
    that lapses unfinished pays the broadcast's penalty, where an unanswered
    one simply expires.
    """
    offer = side_quests.get_offer(db, player, offer_id)
    side_quests.accept_offer(db, player, offer)
    db.commit()
    return offer


@router.post(
    "/{offer_id}/decline",
    response_model=SideQuestOfferResponse,
    summary="Decline a side quest",
)
def decline(
    offer_id: int, player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> SideQuestOffer:
    """Pass on the quest. It costs nothing, now or later.

    Declining a trial of admission withdraws that request to be befriended,
    and starts the same wait a refusal does.
    """
    offer = side_quests.get_offer(db, player, offer_id)
    side_quests.decline_offer(db, player, offer, settings)
    db.commit()
    return offer


@router.post(
    "/{offer_id}/progress",
    response_model=SideQuestProgressResponse,
    summary="Log progress on a side quest",
)
def progress(
    offer_id: int,
    payload: SideQuestProgressRequest,
    player: CurrentPlayer,
    db: DbDep,
    settings: SettingsDep,
) -> SideQuestProgressResponse:
    """Add progress, clearing the side quest if it reaches its target."""
    offer = side_quests.get_offer(db, player, offer_id)
    offer, completed = side_quests.add_progress(
        db, player, offer, payload.amount, settings
    )
    db.commit()

    return SideQuestProgressResponse(
        offer=SideQuestOfferResponse.model_validate(offer), completed=completed
    )


@router.post(
    "/{offer_id}/complete",
    response_model=SideQuestOfferResponse,
    status_code=status.HTTP_200_OK,
    summary="Clear a side quest outright",
)
def complete(
    offer_id: int, player: CurrentPlayer, db: DbDep, settings: SettingsDep
) -> SideQuestOffer:
    """Mark it done without logging each unit, and take the reward."""
    offer = side_quests.get_offer(db, player, offer_id)
    side_quests.complete_offer(db, player, offer, settings)
    db.commit()
    return offer
