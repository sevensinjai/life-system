"""EXP and level arithmetic.

Deliberately pure: no ORM, no session, no clock. Everything here is a function
of its arguments, which keeps the curve easy to test and to retune.
"""

from dataclasses import dataclass

MAX_LEVEL = 999


@dataclass(frozen=True)
class ExpResult:
    """Outcome of applying an EXP change."""

    level: int
    exp: int
    levels_gained: int

    @property
    def leveled_up(self) -> bool:
        return self.levels_gained > 0


def exp_to_next_level(level: int, *, base: int = 100, exponent: float = 1.5) -> int:
    """EXP required to advance from `level` to `level + 1`.

    Rounded to a multiple of ten so the numbers read like a game rather than
    like a floating-point accident.
    """
    if level < 1:
        raise ValueError("level must be at least 1")
    if level >= MAX_LEVEL:
        return 0
    raw = base * (level**exponent)
    return max(10, round(raw / 10) * 10)


def total_exp_for_level(level: int, *, base: int = 100, exponent: float = 1.5) -> int:
    """Cumulative EXP needed to reach `level` from level 1."""
    return sum(
        exp_to_next_level(lv, base=base, exponent=exponent) for lv in range(1, level)
    )


def gain_exp(
    level: int, exp: int, amount: int, *, base: int = 100, exponent: float = 1.5
) -> ExpResult:
    """Add EXP, rolling over into as many levels as the amount covers."""
    if amount < 0:
        raise ValueError("amount must be non-negative; use lose_exp to deduct")

    level, exp = _validate(level, exp)
    exp += amount
    levels_gained = 0

    while level < MAX_LEVEL:
        threshold = exp_to_next_level(level, base=base, exponent=exponent)
        if exp < threshold:
            break
        exp -= threshold
        level += 1
        levels_gained += 1

    if level >= MAX_LEVEL:
        exp = 0

    return ExpResult(level=level, exp=exp, levels_gained=levels_gained)


def lose_exp(level: int, exp: int, amount: int) -> ExpResult:
    """Deduct EXP, clamping at zero.

    A penalty never de-levels the player: progress already banked into a level
    is permanent, and only the EXP toward the next one is at risk. That keeps
    a bad week from erasing months of work.
    """
    if amount < 0:
        raise ValueError("amount must be non-negative")

    level, exp = _validate(level, exp)
    return ExpResult(level=level, exp=max(0, exp - amount), levels_gained=0)


def _validate(level: int, exp: int) -> tuple[int, int]:
    if level < 1:
        raise ValueError("level must be at least 1")
    if exp < 0:
        raise ValueError("exp must be non-negative")
    return level, exp
