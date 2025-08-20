# SPDX-License-Identifier: MIT
import pytest

from dicerealms.core import roll_die


def test_roll_die_range():
    result = roll_die(6)
    assert 1 <= result <= 6
