# SPDX-License-Identifier: MIT
import random
import re


def roll_dice(dice: str) -> int:
    match = re.match(r"(\d+)d(\d+)", dice)
    if not match:
        raise ValueError("Invalid dice format, use NdM (e.g. 2d6)")
    n, m = map(int, match.groups())
    return sum(random.randint(1, m) for _ in range(n))
