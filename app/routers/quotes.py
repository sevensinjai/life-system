"""The quote collection and the one quote a day it surfaces."""

from fastapi import APIRouter, Query, status

from app.deps import CurrentPlayer, DbDep
from app.models import Quote
from app.schemas.quote import (
    DailyQuoteResponse,
    QuoteBulkCreate,
    QuoteBulkResponse,
    QuoteCreate,
    QuoteResponse,
    QuoteUpdate,
)
from app.services import clock
from app.services.quotes import (
    QuoteDraft,
    create_quote,
    create_quotes,
    get_quote,
    list_quotes,
    normalize_text,
    quote_of_the_day,
)

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post(
    "",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Write a quote",
)
def create(payload: QuoteCreate, player: CurrentPlayer, db: DbDep) -> Quote:
    """Add one quote to your collection.

    It joins the rotation immediately, though it will not necessarily be
    today's — see GET /quotes/today.
    """
    quote = create_quote(db, player, text=payload.text, author=payload.author)
    db.commit()
    return quote


@router.post(
    "/bulk",
    response_model=QuoteBulkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Write a batch of quotes",
)
def create_bulk(
    payload: QuoteBulkCreate, player: CurrentPlayer, db: DbDep
) -> QuoteBulkResponse:
    """Add several quotes in one request, skipping any already in rotation.

    Written for the sit-down-and-paste-a-list case. Duplicates are reported
    rather than rejected, so re-importing a list you have partly entered
    before adds only what is new instead of failing the whole request.
    """
    result = create_quotes(
        db,
        player,
        [QuoteDraft(text=item.text, author=item.author) for item in payload.quotes],
    )
    db.commit()

    return QuoteBulkResponse(
        created=[QuoteResponse.model_validate(quote) for quote in result.created],
        created_count=result.created_count,
        skipped_count=result.skipped_count,
        skipped=result.skipped,
    )


@router.get("", response_model=list[QuoteResponse], summary="List your quotes")
def index(
    player: CurrentPlayer,
    db: DbDep,
    include_archived: bool = Query(default=False),
) -> list[Quote]:
    """Your collection, newest first."""
    return list_quotes(db, player, include_archived=include_archived)


@router.get(
    "/today", response_model=DailyQuoteResponse, summary="Today's quote"
)
def today(player: CurrentPlayer, db: DbDep) -> DailyQuoteResponse:
    """The quote to put on the lock screen right now.

    Read-only and stable: asking repeatedly through the day returns the same
    quote, and it turns over at your local midnight. `refresh_after` is when
    that happens, so a widget can schedule its own reload instead of polling.

    An empty collection is not an error — `quote` comes back null so the
    widget can render a prompt to write one.
    """
    local_today = clock.local_date(player.timezone)
    quote, pool_size = quote_of_the_day(db, player, local_today)

    return DailyQuoteResponse(
        local_date=local_today,
        quote=QuoteResponse.model_validate(quote) if quote else None,
        pool_size=pool_size,
        refresh_after=clock.next_local_midnight(player.timezone),
    )


@router.get("/{quote_id}", response_model=QuoteResponse, summary="Fetch one quote")
def show(quote_id: int, player: CurrentPlayer, db: DbDep) -> Quote:
    """Resolve a single quote, archived ones included.

    A widget holding yesterday's id should still be able to render it.
    """
    return get_quote(db, player, quote_id)


@router.patch("/{quote_id}", response_model=QuoteResponse, summary="Edit a quote")
def update(
    quote_id: int, payload: QuoteUpdate, player: CurrentPlayer, db: DbDep
) -> Quote:
    """Reword a quote, re-attribute it, or put it back in rotation."""
    quote = get_quote(db, player, quote_id)

    fields = payload.model_dump(exclude_unset=True)
    if "text" in fields:
        quote.text = normalize_text(fields["text"])
    if "author" in fields:
        quote.author = (fields["author"] or "").strip() or None
    if "is_active" in fields:
        quote.is_active = fields["is_active"]

    db.commit()
    return quote


@router.delete(
    "/{quote_id}", response_model=QuoteResponse, summary="Retire a quote"
)
def archive(quote_id: int, player: CurrentPlayer, db: DbDep) -> Quote:
    """Take a quote out of the rotation without destroying it.

    Deliberately not a hard delete, for the same reason quests archive: a
    widget may still be showing this quote, and it should resolve rather than
    404. Put it back with PATCH is_active=true.
    """
    quote = get_quote(db, player, quote_id)
    quote.is_active = False
    db.commit()
    return quote
