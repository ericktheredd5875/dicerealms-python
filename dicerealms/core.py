# SPDX-License-Identifier: MIT
# dicerealms/core.py
from __future__ import annotations

import random
import re

_DICE_RE = re.compile(r"^\s*(\d+)d(\d+)([+-]\d+)?\s*$", re.I)


def roll_dice(dice: str) -> tuple[int, list[int]]:
    """
    Supports forms like '2d6', '1d20+5', '4d8-2'.
    Returns (total, parts).
    """

    m = _DICE_RE.match(dice)
    if not m:
        raise ValueError(f"Invalid dice format: {dice!r}")

    count, sides, mod = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if count <= 0 or sides <= 1:
        raise ValueError(f"Dice must be NdS with N>0 and S>1: {dice!r}")

    # Applied 'nosec' to random since this is a simple random number generator.
    rolls = [random.randint(1, sides) for _ in range(count)]  # nosec
    total = sum(rolls)
    if mod:
        total += mod

    return total, rolls
