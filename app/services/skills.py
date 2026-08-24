"""The skill graph: shaping it, and rolling EXP up it.

The tree arithmetic at the top is deliberately pure — no ORM, no session — so
the rules that are easy to get wrong (cycles, depth, re-parenting a whole
subtree) can be tested exhaustively against plain dictionaries.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import NotFoundError, ValidationError
from app.models import EventType, Player, Skill
from app.services import leveling
from app.services.progression import log_event

MAX_NAME_LENGTH = 80

# --------------------------------------------------------------------------
# Pure tree arithmetic
# --------------------------------------------------------------------------

ParentMap = Mapping[int, int | None]


def ancestor_ids(parent_of: ParentMap, skill_id: int) -> list[int]:
    """Every ancestor of `skill_id`, nearest parent first.

    Tolerates a malformed map containing a cycle rather than spinning forever:
    it stops as soon as it revisits a node.
    """
    seen: list[int] = []
    current = parent_of.get(skill_id)
    while current is not None and current not in seen:
        seen.append(current)
        current = parent_of.get(current)
    return seen


def depth_of(parent_of: ParentMap, skill_id: int) -> int:
    """How deep a skill sits. A root skill is depth 1."""
    return len(ancestor_ids(parent_of, skill_id)) + 1


def descendant_ids(parent_of: ParentMap, skill_id: int) -> list[int]:
    """Every skill beneath `skill_id`, parents before their children."""
    children: dict[int | None, list[int]] = {}
    for child, parent in parent_of.items():
        children.setdefault(parent, []).append(child)

    found: list[int] = []
    queue = list(children.get(skill_id, ()))
    while queue:
        node = queue.pop(0)
        if node in found:  # a malformed map cannot make this loop
            continue
        found.append(node)
        queue.extend(children.get(node, ()))
    return found


def subtree_height(parent_of: ParentMap, skill_id: int) -> int:
    """How many levels the subtree rooted at `skill_id` occupies.

    A leaf is 1. Needed when re-parenting: moving a three-level subtree under
    a deep node can breach the depth limit even though the moved node itself
    would sit within it.
    """
    below = descendant_ids(parent_of, skill_id)
    if not below:
        return 1
    base = depth_of(parent_of, skill_id)
    return max(depth_of(parent_of, node) for node in below) - base + 1


def would_cycle(parent_of: ParentMap, skill_id: int, new_parent_id: int | None) -> bool:
    """Whether re-parenting would make a skill its own ancestor."""
    if new_parent_id is None:
        return False
    if new_parent_id == skill_id:
        return True
    return skill_id in ancestor_ids(parent_of, new_parent_id)


@dataclass
class TreeNode:
    """A skill and its children, ready to be serialized as a nested tree."""

    skill: Skill
    depth: int
    children: list["TreeNode"] = field(default_factory=list)


def build_forest(skills: Sequence[Skill]) -> list[TreeNode]:
    """Assemble flat rows into nested trees, roots first.

    Rows whose parent is missing from `skills` — an archived parent when the
    caller asked only for active skills — are treated as roots, so filtering
    the graph can never make a skill disappear from it.
    """
    nodes = {skill.id: TreeNode(skill=skill, depth=1) for skill in skills}

    roots: list[TreeNode] = []
    for skill in skills:
        node = nodes[skill.id]
        parent = nodes.get(skill.parent_id) if skill.parent_id else None
        if parent is None:
            roots.append(node)
        else:
            parent.children.append(node)

    def set_depth(node: TreeNode, depth: int) -> None:
        node.depth = depth
        for child in node.children:
            set_depth(child, depth + 1)

    for root in roots:
        set_depth(root, 1)
    return roots


def rollup_shares(amount: int, chain_length: int, rollup: float) -> list[int]:
    """How much EXP each step up the branch receives.

    The skill itself always takes the full amount; each step up multiplies by
    `rollup`, so 1.0 credits the whole branch equally and 0.5 halves it per
    level. Shares are rounded, and the chain stops at the first zero — there
    is no point walking further up once nothing arrives.
    """
    shares: list[int] = []
    for distance in range(chain_length):
        share = amount if distance == 0 else round(amount * rollup**distance)
        if share <= 0:
            break
        shares.append(share)
    return shares


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------


@dataclass
class SkillAward:
    """One skill's share of a single practice or quest completion."""

    skill_id: int
    name: str
    exp_gained: int
    level: int
    levels_gained: int
    distance: int  # 0 for the skill trained, 1 for its parent, and so on

    @property
    def leveled_up(self) -> bool:
        return self.levels_gained > 0


def parent_map(db: Session, player: Player) -> dict[int, int | None]:
    """Every skill the player owns, as child -> parent.

    The whole graph, archived nodes included: the structural rules apply to
    the shape of the tree, not to which parts of it are currently in play.
    """
    rows = db.execute(
        select(Skill.id, Skill.parent_id).where(Skill.player_id == player.id)
    ).all()
    return {row.id: row.parent_id for row in rows}


def get_skill(db: Session, player: Player, skill_id: int) -> Skill:
    """Fetch one of the player's skills, or raise NotFoundError."""
    skill = db.scalar(
        select(Skill).where(Skill.id == skill_id, Skill.player_id == player.id)
    )
    if skill is None:
        raise NotFoundError(f"No skill with id {skill_id}.")
    return skill


def list_skills(
    db: Session, player: Player, *, include_archived: bool = False
) -> list[Skill]:
    """The player's skills, oldest first so a tree renders in authoring order."""
    stmt = select(Skill).where(Skill.player_id == player.id)
    if not include_archived:
        stmt = stmt.where(Skill.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Skill.id)))


def _clean_name(name: str) -> str:
    name = " ".join(name.split())
    if not name:
        raise ValidationError("A skill needs a name.")
    if len(name) > MAX_NAME_LENGTH:
        raise ValidationError(
            f"A skill name may be at most {MAX_NAME_LENGTH} characters."
        )
    return name


def _check_unique_among_siblings(
    db: Session, player: Player, name: str, parent_id: int | None, exclude_id: int = 0
) -> None:
    """Two children of the same parent sharing a name would be unreadable."""
    same_parent = (
        Skill.parent_id.is_(None) if parent_id is None else Skill.parent_id == parent_id
    )
    clash = db.scalar(
        select(Skill).where(
            Skill.player_id == player.id,
            same_parent,
            func.lower(Skill.name) == name.casefold(),
            Skill.id != exclude_id,
        )
    )
    if clash is not None:
        where = "at the top level" if parent_id is None else "under that parent"
        raise ValidationError(f"You already have a skill called {name!r} {where}.")


def _resolve_parent(
    db: Session, player: Player, parent_id: int | None
) -> Skill | None:
    if parent_id is None:
        return None
    parent = get_skill(db, player, parent_id)
    if not parent.is_active:
        raise ValidationError(
            f"{parent.name!r} is archived; restore it before nesting under it."
        )
    return parent


def create_skill(
    db: Session,
    player: Player,
    settings: Settings,
    *,
    name: str,
    description: str | None = None,
    parent_id: int | None = None,
) -> Skill:
    """Add a skill, optionally beneath one that already exists."""
    name = _clean_name(name)
    _resolve_parent(db, player, parent_id)

    if parent_id is not None:
        depth = depth_of(parent_map(db, player), parent_id) + 1
        if depth > settings.max_skill_depth:
            raise ValidationError(
                f"That would nest the skill {depth} deep; the limit is "
                f"{settings.max_skill_depth}."
            )

    _check_unique_among_siblings(db, player, name, parent_id)

    skill = Skill(
        player_id=player.id,
        parent_id=parent_id,
        name=name,
        description=description,
    )
    db.add(skill)
    db.flush()

    log_event(
        db,
        player,
        EventType.SKILL_CREATED,
        f"New skill unlocked: {skill.name}",
        {"skill_id": skill.id, "parent_id": parent_id},
    )
    return skill


def rename(db: Session, player: Player, skill: Skill, name: str) -> str:
    """Validate a new name against the skill's siblings and return it cleaned."""
    name = _clean_name(name)
    _check_unique_among_siblings(
        db, player, name, skill.parent_id, exclude_id=skill.id
    )
    return name


def reparent(
    db: Session,
    player: Player,
    skill: Skill,
    settings: Settings,
    new_parent_id: int | None,
) -> Skill:
    """Move a skill — and everything under it — somewhere else in the tree."""
    if new_parent_id == skill.parent_id:
        return skill

    _resolve_parent(db, player, new_parent_id)
    parents = parent_map(db, player)

    if would_cycle(parents, skill.id, new_parent_id):
        raise ValidationError(
            "That move would make the skill its own ancestor."
        )

    new_depth = 1 if new_parent_id is None else depth_of(parents, new_parent_id) + 1
    height = subtree_height(parents, skill.id)
    if new_depth + height - 1 > settings.max_skill_depth:
        raise ValidationError(
            f"That move would push the branch to {new_depth + height - 1} deep; "
            f"the limit is {settings.max_skill_depth}."
        )

    _check_unique_among_siblings(
        db, player, skill.name, new_parent_id, exclude_id=skill.id
    )

    skill.parent_id = new_parent_id
    return skill


def set_active(db: Session, player: Player, skill: Skill, active: bool) -> list[Skill]:
    """Archive a skill with its subtree, or restore it with its ancestors.

    Both directions preserve one invariant: an active skill never hangs under
    an archived parent. Archiving therefore takes the branch below with it,
    and restoring pulls the branch above back.
    """
    parents = parent_map(db, player)
    if active:
        ids = [skill.id, *ancestor_ids(parents, skill.id)]
    else:
        ids = [skill.id, *descendant_ids(parents, skill.id)]

    affected = list(
        db.scalars(select(Skill).where(Skill.id.in_(ids), Skill.player_id == player.id))
    )
    for node in affected:
        node.is_active = active
    return affected


def award_skill_exp(
    db: Session,
    player: Player,
    skill: Skill,
    amount: int,
    settings: Settings,
    *,
    source: str = "",
) -> list[SkillAward]:
    """Grant EXP to a skill and roll it up the branch above.

    Practising a sub-skill is practising its parent, so the whole ancestry is
    credited. Returns one award per skill touched, nearest first, which is
    what the client animates.
    """
    if amount < 0:
        raise ValidationError("Skill EXP award must be non-negative.")
    if amount == 0:
        return []
    if not skill.is_active:
        raise ValidationError(
            f"{skill.name!r} is archived; restore it before training it."
        )

    parents = parent_map(db, player)
    chain_ids = [skill.id, *ancestor_ids(parents, skill.id)]
    shares = rollup_shares(amount, len(chain_ids), settings.skill_exp_rollup)

    by_id = {
        node.id: node
        for node in db.scalars(
            select(Skill).where(
                Skill.id.in_(chain_ids[: len(shares)]), Skill.player_id == player.id
            )
        )
    }

    awards: list[SkillAward] = []
    for distance, (skill_id, share) in enumerate(zip(chain_ids, shares)):
        node = by_id.get(skill_id)
        if node is None:
            continue

        result = leveling.gain_exp(
            node.level,
            node.exp,
            share,
            base=settings.skill_exp_curve_base,
            exponent=settings.skill_exp_curve_exponent,
        )
        node.level = result.level
        node.exp = result.exp
        node.total_exp_earned += share

        if result.leveled_up:
            log_event(
                db,
                player,
                EventType.SKILL_LEVEL_UP,
                f"{node.name} reached Lv. {node.level}.",
                {
                    "skill_id": node.id,
                    "new_level": node.level,
                    "levels_gained": result.levels_gained,
                    "exp_gained": share,
                    "source": source,
                },
            )

        awards.append(
            SkillAward(
                skill_id=node.id,
                name=node.name,
                exp_gained=share,
                level=node.level,
                levels_gained=result.levels_gained,
                distance=distance,
            )
        )
    return awards


def award_for_quest(
    db: Session, player: Player, quest, settings: Settings
) -> list[SkillAward]:
    """The skill payout for clearing a quest, if it names one.

    A quest pointing at a skill the player has since archived pays out nothing
    rather than failing the completion: clearing the quest is still valid, it
    just trains nothing.
    """
    if quest.skill_id is None or quest.skill_exp_reward <= 0:
        return []

    skill = db.scalar(
        select(Skill).where(
            Skill.id == quest.skill_id, Skill.player_id == player.id
        )
    )
    if skill is None or not skill.is_active:
        return []

    return award_skill_exp(
        db,
        player,
        skill,
        quest.skill_exp_reward,
        settings,
        source=f"quest:{quest.id}",
    )


def practice(
    db: Session,
    player: Player,
    skill: Skill,
    amount: int,
    settings: Settings,
) -> list[SkillAward]:
    """Log practice that no quest covers."""
    if amount <= 0:
        raise ValidationError("Practice EXP must be positive.")
    return award_skill_exp(db, player, skill, amount, settings, source="practice")


def exp_to_next(skill: Skill, settings: Settings) -> int:
    return leveling.exp_to_next_level(
        skill.level,
        base=settings.skill_exp_curve_base,
        exponent=settings.skill_exp_curve_exponent,
    )
