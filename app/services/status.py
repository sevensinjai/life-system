"""Assembling the status window the client renders."""

from app.config import Settings
from app.models import Player
from app.schemas.player import PlayerStatus, StatBlock
from app.services import leveling


def build_player_status(player: Player, settings: Settings) -> PlayerStatus:
    """Project a Player into its status-window representation."""
    to_next = leveling.exp_to_next_level(
        player.level,
        base=settings.exp_curve_base,
        exponent=settings.exp_curve_exponent,
    )
    progress = round(player.exp / to_next, 4) if to_next > 0 else 1.0

    return PlayerStatus(
        id=player.id,
        name=player.name,
        level=player.level,
        exp=player.exp,
        exp_to_next_level=to_next,
        exp_progress=progress,
        total_exp_earned=player.total_exp_earned,
        stat_points=player.stat_points,
        stats=StatBlock(
            strength=player.strength,
            agility=player.agility,
            vitality=player.vitality,
            intelligence=player.intelligence,
            perception=player.perception,
        ),
        timezone=player.timezone,
    )
