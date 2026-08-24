"""ORM models. Importing this package registers every table on Base.metadata."""

from app.models.constellation import Constellation, ConstellationFavor
from app.models.enums import (
    DIFFICULTY_EXP,
    MAX_FAVOR,
    MIN_FAVOR,
    SIDE_QUEST_OFFERS_PER_WEEK,
    STANDING_THRESHOLDS,
    EventType,
    QuestDifficulty,
    QuestStatus,
    ScheduleKind,
    SideQuestFrequency,
    SideQuestOfferStatus,
    SideQuestStatus,
    Standing,
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
    "MAX_FAVOR",
    "MIN_FAVOR",
    "SIDE_QUEST_OFFERS_PER_WEEK",
    "STANDING_THRESHOLDS",
    "Constellation",
    "ConstellationFavor",
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
    "Standing",
    "StatName",
    "SystemEvent",
    "User",
]
