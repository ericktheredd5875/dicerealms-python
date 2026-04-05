# SPDX-License-Identifier: MIT
"""Tests for core dice rolling logic."""
import pytest

from dicerealms.core import roll_dice

class TestRollDice:
    """
    Test Suite for roll_dice.
    """

    def test_basic_roll_returns_tuple(self):
        total, parts = roll_dice("2d6")
        assert isinstance(total, int)
        assert isinstance(parts, list)
        assert len(parts) == 2

    def test_parts_within_di_range(self):
        _, parts = roll_dice("4d8")
        assert all(1 <= p <= 8 for p in parts)

    def test_total_equals_sum_of_parts_no_modifier(self):
        total, parts = roll_dice("3d6")
        assert total == sum(parts)

    def test_positive_modifier_applied(self):
        total, parts = roll_dice("2d6+5")
        assert total == sum(parts) + 5

    def test_negative_modifier_applied(self):
        total, parts = roll_dice("2d6-2")
        assert total == sum(parts) - 2

    def test_single_die(self):
        total, parts = roll_dice("1d20")
        assert len(parts) == 1
        assert 1 <= total <= 20

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            roll_dice("invalid")

    def test_zero_count_raises(self):
        with pytest.raises(ValueError):
            roll_dice("0d6")

    def test_one_sided_die_raises(self):
        with pytest.raises(ValueError):
            roll_dice("1d1")

    def test_case_insensitive(self):
        total, parts = roll_dice("2D6")
        assert len(parts) == 2