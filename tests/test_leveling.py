"""The EXP curve and level arithmetic."""

import pytest

from app.services.leveling import (
    MAX_LEVEL,
    exp_to_next_level,
    gain_exp,
    lose_exp,
    total_exp_for_level,
)


def test_curve_is_monotonically_increasing() -> None:
    thresholds = [exp_to_next_level(level) for level in range(1, 50)]
    assert thresholds == sorted(thresholds)
    assert all(t % 10 == 0 for t in thresholds)


def test_first_level_costs_the_base() -> None:
    assert exp_to_next_level(1, base=100, exponent=1.5) == 100


def test_level_below_one_is_rejected() -> None:
    with pytest.raises(ValueError):
        exp_to_next_level(0)


def test_gain_below_threshold_does_not_level() -> None:
    result = gain_exp(1, 0, 99)
    assert (result.level, result.exp, result.leveled_up) == (1, 99, False)


def test_gain_exactly_threshold_levels_once() -> None:
    result = gain_exp(1, 0, 100)
    assert (result.level, result.exp, result.levels_gained) == (2, 0, 1)


def test_large_gain_cascades_multiple_levels() -> None:
    result = gain_exp(1, 0, 500)
    # 100 to reach L2, 280 to reach L3, leaving 120 toward L4.
    assert (result.level, result.exp, result.levels_gained) == (3, 120, 2)


def test_gain_carries_existing_exp() -> None:
    result = gain_exp(1, 60, 40)
    assert (result.level, result.exp) == (2, 0)


def test_gain_rejects_negative() -> None:
    with pytest.raises(ValueError):
        gain_exp(1, 0, -1)


def test_loss_clamps_at_zero_and_never_delevels() -> None:
    result = lose_exp(5, 30, 500)
    assert (result.level, result.exp) == (5, 0)


def test_loss_deducts_partially() -> None:
    result = lose_exp(3, 200, 50)
    assert (result.level, result.exp) == (3, 150)


def test_total_exp_for_level_sums_the_curve() -> None:
    assert total_exp_for_level(1) == 0
    assert total_exp_for_level(2) == exp_to_next_level(1)
    assert total_exp_for_level(4) == sum(exp_to_next_level(lv) for lv in (1, 2, 3))


def test_max_level_absorbs_further_exp() -> None:
    result = gain_exp(MAX_LEVEL, 0, 10**9)
    assert result.level == MAX_LEVEL
    assert result.exp == 0
    assert exp_to_next_level(MAX_LEVEL) == 0
