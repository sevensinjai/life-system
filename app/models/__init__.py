"""ORM models. Importing this package registers every table on Base.metadata."""

from app.models.enums import (
    DIFFICULTY_EXP,
    SIDE_QUEST_OFFERS_PER_WEEK,
    EventType,
    QuestDifficulty,
    QuestStatus,
    ScheduleKind,
    SideQuestFrequency,
    SideQuestOfferStatus,
    SideQuestStatus,
    StatName,
)
from app.models.event import SystemEvent
from app.models.player import Player
from app.models.quest import Penalty, Quest, QuestInstance
from app.models.quote import Quote
from app.models.side_quest import SideQuest, SideQuestOffer, SideQuestPreference
from app.models.user import User

__all__ = [
    "DIFFICULTY_EXP",
    "SIDE_QUEST_OFFERS_PER_WEEK",
    "EventType",
    "Penalty",
    "Player",
    "Quest",
    "QuestDifficulty",
    "QuestInstance",
    "QuestStatus",
    "Quote",
    "ScheduleKind",
    "SideQuest",
    "SideQuestFrequency",
    "SideQuestOffer",
    "SideQuestOfferStatus",
    "SideQuestPreference",
    "SideQuestStatus",
    "StatName",
    "SystemEvent",
    "User",
]
