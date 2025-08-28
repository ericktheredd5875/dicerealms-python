# SPDX-License-Identifier: MIT
# tests/test_core.py
import pytest

from dicerealms.core import roll_dice


def test_roll_die_range():
    total, parts = roll_dice("1d6")
    assert 1 <= total <= 6


def test_roll_die_valid_basic(monkeypatch):
    # Make rnadomness deterministic
    seq = [3, 4]
    it = iter(seq)
    monkeypatch.setattr("random.randint", lambda a, b: next(it))
    total, parts = roll_dice("2d6")
    assert parts == seq
    assert total == sum(seq)


@pytest.mark.parametrize("bad", ["", "d6", "0d6", "2d1", "2dx", "2d6++1"])
def test_roll_invalid_inputs(bad):
    with pytest.raises(ValueError):
        roll_dice(bad)
