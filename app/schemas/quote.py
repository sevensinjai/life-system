"""Request and response models for the quote collection."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.services.quotes import (
    MAX_AUTHOR_LENGTH,
    MAX_BULK_QUOTES,
    MAX_QUOTE_LENGTH,
)


class QuoteCreate(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=MAX_QUOTE_LENGTH,
        examples=["Arise."],
        description="The line itself. Surrounding and repeated whitespace is collapsed.",
    )
    author: str | None = Field(
        default=None,
        max_length=MAX_AUTHOR_LENGTH,
        description="Who said it. Leave it out for something you wrote yourself.",
    )


class QuoteBulkCreate(BaseModel):
    """Write a batch of quotes in one request."""

    quotes: list[QuoteCreate] = Field(min_length=1, max_length=MAX_BULK_QUOTES)


class QuoteUpdate(BaseModel):
    """Edit a quote. Omitted fields are left alone."""

    text: str | None = Field(default=None, min_length=1, max_length=MAX_QUOTE_LENGTH)
    author: str | None = Field(default=None, max_length=MAX_AUTHOR_LENGTH)
    is_active: bool | None = Field(
        default=None, description="Set false to take it out of the rotation."
    )


class QuoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    author: str | None
    is_active: bool
    created_at: datetime


class QuoteBulkResponse(BaseModel):
    """The outcome of a batch write, including what it declined to duplicate."""

    created: list[QuoteResponse]
    created_count: int
    skipped_count: int = Field(
        description="Quotes already in the rotation, which were not added again."
    )
    skipped: list[str] = Field(
        default_factory=list, description="The text of each skipped duplicate."
    )


class DailyQuoteResponse(BaseModel):
    """The one quote for today — what the lock-screen widget renders."""

    local_date: date = Field(
        description="The date this quote belongs to, in the player's timezone."
    )
    quote: QuoteResponse | None = Field(
        default=None, description="Null when the collection is empty."
    )
    pool_size: int = Field(description="How many quotes are currently in rotation.")
    refresh_after: datetime = Field(
        description=(
            "When today's quote gives way to tomorrow's, in UTC — the player's "
            "next local midnight. Schedule the widget's next reload for this."
        )
    )
