"""The pantheon in the database: seeding it, and keeping its regard.

The pure half of this — what an ending is worth, which band a score falls
into, which line gets said — lives in `services/story.py`. This module is the
part that touches rows: loading the written pantheon in, finding the favor
record between one player and one constellation, and moving it when a side
quest ends.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.pantheon import (
    PANTHEON,
    SYSTEM_VOICE,
    ConstellationEntry,
    as_voice_payload,
)
from app.errors import NotFoundError
from app.models import (
    Constellation,
    ConstellationFavor,
    Player,
    QuestDifficulty,
    SideQuest,
    SideQuestOfferStatus,
    Standing,
)
from app.services import clock, story


@dataclass
class SeedResult:
    """What one run of the seeder changed."""

    created: list[str]
    updated: list[str]

    @property
    def created_count(self) -> int:
        return len(self.created)

    @property
    def updated_count(self) -> int:
        return len(self.updated)


def seed_pantheon(
    db: Session, entries: tuple[ConstellationEntry, ...] = PANTHEON
) -> SeedResult:
    """Load the written pantheon into the database, idempotently.

    Matched on `code`, so rewriting a constellation's name or voice updates
    the row in place and leaves every favor record pointing at the same
    character. Nothing is deleted: a constellation dropped from the catalog
    keeps its history, and is retired by hand.
    """
    result = SeedResult(created=[], updated=[])

    for entry in entries:
        existing = db.scalar(
            select(Constellation).where(Constellation.code == entry.code)
        )
        voice = as_voice_payload(entry)

        if existing is None:
            db.add(Constellation(code=entry.code, voice=voice, **_written_fields(entry)))
            result.created.append(entry.code)
            continue

        written = _written_fields(entry)
        changed = existing.voice != voice or any(
            getattr(existing, field) != value for field, value in written.items()
        )
        if changed:
            for field, value in written.items():
                setattr(existing, field, value)
            existing.voice = voice
            result.updated.append(entry.code)

    db.flush()
    return result


def _written_fields(entry: ConstellationEntry) -> dict:
    """The columns the catalog owns — everything a rewrite may change.

    Named in one place so adding a field to the written pantheon cannot be
    half-applied: the seeder writes and compares the same set.
    """
    return {
        "code_name": entry.code_name,
        "code_name_zh_hant": entry.code_name_zh_hant,
        "real_name": entry.real_name,
        "real_name_zh_hant": entry.real_name_zh_hant,
        "epithet": entry.epithet,
        "epithet_zh_hant": entry.epithet_zh_hant,
        "description": entry.description,
        "domain": entry.domain,
    }


def get_by_code(db: Session, code: str) -> Constellation:
    """Fetch one constellation by its stable code, or raise NotFoundError."""
    constellation = db.scalar(
        select(Constellation).where(Constellation.code == code)
    )
    if constellation is None:
        raise NotFoundError(f"No constellation with code {code!r}.")
    return constellation


def list_constellations(
    db: Session, *, include_retired: bool = False
) -> list[Constellation]:
    """The pantheon, in a stable order."""
    stmt = select(Constellation)
    if not include_retired:
        stmt = stmt.where(Constellation.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Constellation.id)))


def default_favor(player: Player, constellation: Constellation) -> ConstellationFavor:
    """A blank history, for two that have never met.

    Transient on purpose: no row means no history, so reading a standing must
    not quietly create one. Every counter is set here rather than left to the
    column defaults, which only fire on insert — a record that is never saved
    still has to read as zeros rather than as nulls.
    """
    return ConstellationFavor(
        constellation_id=constellation.id,
        player_id=player.id,
        favor=0,
        is_friend=False,
        may_ask_after=None,
        offers_received=0,
        completed=0,
        declined=0,
        expired=0,
        failed=0,
    )


def get_favor(
    db: Session, player: Player, constellation: Constellation
) -> ConstellationFavor:
    """The record between these two, real or blank."""
    stored = db.scalar(
        select(ConstellationFavor).where(
            ConstellationFavor.constellation_id == constellation.id,
            ConstellationFavor.player_id == player.id,
        )
    )
    return stored if stored is not None else default_favor(player, constellation)


def ensure_favor(
    db: Session, player: Player, constellation: Constellation
) -> ConstellationFavor:
    """The record between these two, created if this is their first meeting."""
    stored = db.scalar(
        select(ConstellationFavor).where(
            ConstellationFavor.constellation_id == constellation.id,
            ConstellationFavor.player_id == player.id,
        )
    )
    if stored is None:
        stored = default_favor(player, constellation)
        db.add(stored)
        db.flush()
    return stored


def standing_of(
    db: Session, player: Player, constellation: Constellation | None
) -> Standing:
    """Where the player stands with this constellation right now.

    A broadcast with nobody behind it has no standing to speak of, so it reads
    as STRANGER — the band everyone starts in.
    """
    if constellation is None:
        return Standing.STRANGER
    return story.standing_for(get_favor(db, player, constellation).favor)


def record_offer(
    db: Session,
    player: Player,
    constellation: Constellation | None,
    *,
    now: datetime | None = None,
) -> ConstellationFavor | None:
    """Note that these two have now met. Favor itself does not move."""
    if constellation is None:
        return None
    now = now or clock.utcnow()

    favor = ensure_favor(db, player, constellation)
    favor.offers_received += 1
    if favor.first_seen_at is None:
        favor.first_seen_at = now
    favor.last_seen_at = now
    return favor


@dataclass
class FavorChange:
    """One movement in a constellation's regard."""

    constellation: Constellation
    before: int
    after: int
    standing_before: Standing
    standing_after: Standing

    @property
    def delta(self) -> int:
        return self.after - self.before

    @property
    def band_changed(self) -> bool:
        return self.standing_before is not self.standing_after


def record_outcome(
    db: Session,
    player: Player,
    constellation: Constellation | None,
    status: SideQuestOfferStatus,
    difficulty: QuestDifficulty,
    *,
    now: datetime | None = None,
) -> FavorChange | None:
    """Move a constellation's regard to match how a side quest ended.

    Never touches EXP, levels, or stats — that separation is the whole reason
    favor can be harsh without the opt-in becoming a trap.
    """
    if constellation is None:
        return None
    now = now or clock.utcnow()

    favor = ensure_favor(db, player, constellation)
    before = favor.favor
    standing_before = story.standing_for(before)

    match status:
        case SideQuestOfferStatus.COMPLETED:
            favor.completed += 1
        case SideQuestOfferStatus.DECLINED:
            favor.declined += 1
        case SideQuestOfferStatus.EXPIRED:
            favor.expired += 1
        case SideQuestOfferStatus.FAILED:
            favor.failed += 1

    favor.favor = story.clamp_favor(before + story.favor_delta(status, difficulty))
    favor.last_seen_at = now

    return FavorChange(
        constellation=constellation,
        before=before,
        after=favor.favor,
        standing_before=standing_before,
        standing_after=story.standing_for(favor.favor),
    )


def line_for(
    side_quest: SideQuest,
    constellation: Constellation | None,
    kind: str,
    standing: Standing,
    *,
    seed: int = 0,
) -> str | None:
    """What is said when `kind` happens, from whoever has something to say.

    The broadcast's own line wins, then the constellation's voice, then the
    plain System register — so a trial can have a closing line of its own
    without every trial needing one.
    """
    return story.pick_line(
        kind,
        standing,
        overrides=side_quest.lines,
        voice=constellation.voice if constellation else None,
        fallback=SYSTEM_VOICE,
        seed=seed,
    )
