# tests/test_core_enhanced.py
# SPDX-License-Identifier: MIT

from unittest.mock import patch

import pytest

from dicerealms.core import _DICE_RE, roll_dice


def test_dice_regex_patterns():
    """Test the dice regex with various valid patterns."""
    valid_patterns = [
        "1d6",
        "2d6",
        "10d20",
        "1d100",
        "1d6+1",
        "2d6-1",
        "3d8+5",
        "1d20-3",
        " 1d6 ",
        " 2d6+1 ",
        " 3d8-2 ",
        "1D6",
        "2D6+1",
        "3D8-2",  # Case insensitive
    ]

    for pattern in valid_patterns:
        assert _DICE_RE.match(pattern) is not None, f"Pattern {pattern} should match"


def test_dice_regex_invalid_patterns():
    """Test the dice regex with invalid patterns."""
    # Note: 0d6 and 2d1 match the regex but fail validation later
    invalid_patterns = [
        "",
        "d6",
        "2dx",
        "2d6++1",
        "1d6+",
        "1d6-",
        "1d6+1+1",
        "1d6-1-1",
        "1d6*2",
        "1d6/2",
        "1d6^2",
        "1d6%2",
    ]

    for pattern in invalid_patterns:
        assert _DICE_RE.match(pattern) is None, f"Pattern {pattern} should not match"


@pytest.mark.parametrize(
    "dice_expr,expected_total_range,expected_parts_count",
    [
        ("1d6", (1, 6), 1),
        ("2d6", (2, 12), 2),
        ("3d8", (3, 24), 3),
        ("1d20", (1, 20), 1),
    ],
)
def test_roll_dice_range_and_count(
    dice_expr, expected_total_range, expected_parts_count
):
    """Test that dice rolls are within expected ranges and have correct part counts."""
    total, parts = roll_dice(dice_expr)

    min_total, max_total = expected_total_range
    assert min_total <= total <= max_total
    assert len(parts) == expected_parts_count
    assert all(1 <= part <= int(dice_expr.split("d")[1]) for part in parts)


@pytest.mark.parametrize(
    "dice_expr,modifier",
    [
        ("1d6+1", 1),
        ("1d6-1", -1),
        ("1d6+5", 5),
        ("1d6-3", -3),
        ("1d6+0", 0),
    ],
)
def test_roll_dice_with_modifiers(dice_expr, modifier):
    """Test dice rolling with modifiers."""
    with patch("random.randint", return_value=3):
        total, parts = roll_dice(dice_expr)
        expected_total = 3 + modifier
        assert total == expected_total
        assert parts == [3]


@pytest.mark.parametrize(
    "dice_expr,count,sides,mod",
    [
        ("1d6", 1, 6, 0),
        ("2d6+1", 2, 6, 1),
        ("3d8-2", 3, 8, -2),
        ("1d20+5", 1, 20, 5),
    ],
)
def test_roll_dice_parsing(dice_expr, count, sides, mod):
    """Test that dice expressions are parsed correctly."""
    match = _DICE_RE.match(dice_expr)
    assert match is not None

    parsed_count = int(match.group(1))
    parsed_sides = int(match.group(2))
    parsed_mod = int(match.group(3) or 0)

    assert parsed_count == count
    assert parsed_sides == sides
    assert parsed_mod == mod


def test_roll_dice_deterministic_with_mock():
    """Test dice rolling with mocked random for deterministic results."""
    with patch("random.randint", side_effect=[4, 3, 6]):
        total, parts = roll_dice("3d6")
        assert total == 13
        assert parts == [4, 3, 6]


def test_roll_dice_with_modifier_deterministic():
    """Test dice rolling with modifier using mocked random."""
    with patch("random.randint", return_value=5):
        total, parts = roll_dice("1d6+2")
        assert total == 7
        assert parts == [5]


def test_roll_dice_negative_modifier():
    """Test dice rolling with negative modifier."""
    with patch("random.randint", return_value=4):
        total, parts = roll_dice("1d6-2")
        assert total == 2
        assert parts == [4]


def test_roll_dice_zero_modifier():
    """Test dice rolling with zero modifier."""
    with patch("random.randint", return_value=3):
        total, parts = roll_dice("1d6+0")
        assert total == 3
        assert parts == [3]


@pytest.mark.parametrize(
    "invalid_dice",
    [
        "",
        "d6",
        "0d6",  # This matches regex but fails validation
        "2d1",  # This matches regex but fails validation
        "2dx",
        "2d6++1",
        "1d6+",
        "1d6-",
        "1d6*2",
        "1d6/2",
        "abc",
        "1d",
        "d",
        "1d6+1+1",
        "1d6-1-1",
    ],
)
def test_roll_dice_invalid_inputs(invalid_dice):
    """Test that invalid dice expressions raise ValueError."""
    with pytest.raises(ValueError):
        roll_dice(invalid_dice)


def test_roll_dice_edge_cases():
    """Test edge cases for dice rolling."""
    # Test minimum valid dice
    total, parts = roll_dice("1d2")
    assert 1 <= total <= 2
    assert len(parts) == 1

    # Test large dice
    total, parts = roll_dice("1d100")
    assert 1 <= total <= 100
    assert len(parts) == 1


def test_roll_dice_case_insensitive():
    """Test that dice expressions are case insensitive."""
    with patch("random.randint", return_value=4):
        total1, parts1 = roll_dice("1d6")
        total2, parts2 = roll_dice("1D6")

        assert total1 == total2
        assert parts1 == parts2


def test_roll_dice_whitespace_handling():
    """Test that dice expressions handle whitespace correctly."""
    with patch("random.randint", return_value=3):
        total1, parts1 = roll_dice("1d6")
        total2, parts2 = roll_dice(" 1d6 ")
        total3, parts3 = roll_dice("1d6+1")
        total4, parts4 = roll_dice(" 1d6+1 ")

        assert total1 == total2
        assert parts1 == parts2
        assert total3 == total4
        assert parts3 == parts4
