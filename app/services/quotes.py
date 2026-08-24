"""The quote collection, and the rotation that puts one on the lock screen.

`pick_for_day` is deliberately pure — no ORM, no clock, no settings — which is
what makes the rotation cheap to test exhaustively and safe to retune.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.models import Player, Quote

MAX_QUOTE_LENGTH = 500
MAX_AUTHOR_LENGTH = 120
# A ceiling on one bulk request, not on the collection itself.
MAX_BULK_QUOTES = 100


@dataclass(frozen=True)
class QuoteDraft:
    """One quote as authored, before it becomes a row."""

    text: str
    author: str | None = None


@dataclass
class BulkResult:
    """What one bulk create actually did."""

    created: list[Quote] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def created_count(self) -> int:
        return len(self.created)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped)


def normalize_text(text: str) -> str:
    """Collapse whitespace so two copies of the same line compare equal.

    Quotes arrive pasted from all over — a line break mid-sentence should not
    make a duplicate look like a new quote.
    """
    return " ".join(text.split())


def pick_for_day(quote_ids: Sequence[int], day: date) -> int | None:
    """Which quote the given day lands on.

    A rotation rather than a random draw, for two reasons: the same day always
    resolves to the same quote no matter how often a widget asks, and
    consecutive days step through the pool in order, so every quote is seen
    once before any of them repeats.

    Adding or archiving a quote changes the pool and so reshuffles which quote
    future days land on. That is the cost of storing no state; today's answer
    stays fixed for as long as the pool does.
    """
    if not quote_ids:
        return None
    return quote_ids[day.toordinal() % len(quote_ids)]


def _validate(text: str, author: str | None) -> tuple[str, str | None]:
    text = normalize_text(text)
    if not text:
        raise ValidationError("A quote needs some text.")
    if len(text) > MAX_QUOTE_LENGTH:
        raise ValidationError(
            f"A quote may be at most {MAX_QUOTE_LENGTH} characters; "
            f"this one is {len(text)}."
        )

    author = (author or "").strip() or None
    if author is not None and len(author) > MAX_AUTHOR_LENGTH:
        raise ValidationError(
            f"An author may be at most {MAX_AUTHOR_LENGTH} characters."
        )
    return text, author


def create_quote(
    db: Session, player: Player, *, text: str, author: str | None = None
) -> Quote:
    """Add one quote to the player's collection."""
    text, author = _validate(text, author)

    quote = Quote(player_id=player.id, text=text, author=author)
    db.add(quote)
    db.flush()
    return quote


def create_quotes(
    db: Session, player: Player, drafts: Iterable[QuoteDraft]
) -> BulkResult:
    """Add several quotes at once, skipping ones already in the rotation.

    Writing quotes is a sit-down-and-paste-a-list activity, so the same line
    arriving twice is likelier to be a re-import than a deliberate duplicate.
    Matching is case-insensitive and ignores the author: the same words by a
    different attribution are still the same quote on a lock screen.

    Only active quotes are matched against — re-adding something you archived
    puts it back in rotation rather than silently doing nothing.
    """
    drafts = list(drafts)
    if not drafts:
        raise ValidationError("Provide at least one quote.")
    if len(drafts) > MAX_BULK_QUOTES:
        raise ValidationError(
            f"At most {MAX_BULK_QUOTES} quotes per request; got {len(drafts)}."
        )

    seen = {
        quote.text.casefold()
        for quote in list_quotes(db, player, include_archived=False)
    }

    result = BulkResult()
    for draft in drafts:
        text, author = _validate(draft.text, draft.author)
        key = text.casefold()
        if key in seen:
            result.skipped.append(text)
            continue
        seen.add(key)
        result.created.append(create_quote(db, player, text=text, author=author))
    return result


def get_quote(db: Session, player: Player, quote_id: int) -> Quote:
    """Fetch one of the player's quotes, or raise NotFoundError."""
    quote = db.scalar(
        select(Quote).where(Quote.id == quote_id, Quote.player_id == player.id)
    )
    if quote is None:
        raise NotFoundError(f"No quote with id {quote_id}.")
    return quote


def list_quotes(
    db: Session, player: Player, *, include_archived: bool = False
) -> list[Quote]:
    """The player's quotes, newest first."""
    stmt = select(Quote).where(Quote.player_id == player.id)
    if not include_archived:
        stmt = stmt.where(Quote.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Quote.created_at.desc(), Quote.id.desc())))


def rotation_ids(db: Session, player: Player) -> list[int]:
    """The ids in rotation, oldest first.

    Ordered by id rather than by creation time so the rotation is stable: two
    quotes written in the same second must still have one fixed order.
    """
    return list(
        db.scalars(
            select(Quote.id)
            .where(Quote.player_id == player.id, Quote.is_active.is_(True))
            .order_by(Quote.id)
        )
    )


def quote_of_the_day(
    db: Session, player: Player, today: date
) -> tuple[Quote | None, int]:
    """The quote to show on `today`, plus how many are in rotation.

    Returns no quote rather than raising when the collection is empty — a
    widget with nothing to show should render a prompt to write one, not an
    error.
    """
    ids = rotation_ids(db, player)
    chosen = pick_for_day(ids, today)
    quote = db.get(Quote, chosen) if chosen is not None else None
    return quote, len(ids)
