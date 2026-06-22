# SPDX-License-Identifier: MIT
from dataclasses import dataclass


@dataclass
class Player:
    name: str = "Adventurer"
    room: str = "town_square"
    hp: int = 20
    max_hp: int = 20
    mp: int = 10
    max_mp: int = 10
    level: int = 1
    xp: int = 0
