"""Response models for the system log and the daily reset."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import EventType


class SystemEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: EventType
    message: str
    payload: dict[str, Any]
    created_at: datetime


class PenaltyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reason: str
    exp_lost: int
    created_at: datetime


class DailyResetResponse(BaseModel):
    reset_date: date
    failed_count: int
    spawned_count: int
    total_exp_lost: int
