"""Shared response types."""

from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator

from app.services.clock import as_utc

# Every timestamp in this app is UTC, but SQLite hands them back with no
# timezone attached, and a client that reads a deadline as local time is wrong
# by hours. Stamping on the way out keeps "timestamps are UTC" true in the
# JSON as well as in the database, whatever the backend returned.
UtcMoment = Annotated[datetime, AfterValidator(as_utc)]
