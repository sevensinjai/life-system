"""The skill graph: what the player is training, and how good they are at it."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.player import Player


class Skill(Base):
    """One node in the player's skill tree.

    A skill owns its level and EXP the same way the player does, and nests to
    any depth: Singing holds Pitch accuracy, which can hold Interval jumps.
    Practising a leaf rolls EXP up the branch, so a parent levels off the work
    done inside it.

    A tree rather than a general graph — one parent each — because that gives
    every skill exactly one path to its root, which is what makes rolling EXP
    upward unambiguous. Two parents would mean an ancestor could be credited
    twice for the same practice.
    """

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )
    # Null for a root skill. Deleting a parent takes its subtree with it.
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=True, index=True
    )

    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_key: Mapped[str | None] = mapped_column(String(120), nullable=True)

    level: Mapped[int] = mapped_column(Integer, default=1)
    # EXP toward the NEXT level, not a lifetime total — as on Player.
    exp: Mapped[int] = mapped_column(Integer, default=0)
    total_exp_earned: Mapped[int] = mapped_column(Integer, default=0)

    # An archived skill leaves the graph: it takes no practice and receives no
    # roll-up. Its subtree is archived with it, so an active skill never hangs
    # under an archived parent.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    player: Mapped["Player"] = relationship(back_populates="skills")
    parent: Mapped["Skill | None"] = relationship(
        back_populates="children", remote_side="Skill.id"
    )
    children: Mapped[list["Skill"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name!r} level={self.level}>"
