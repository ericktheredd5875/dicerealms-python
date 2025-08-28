# SPDX-License-Identifier: MIT
from dataclasses import dataclass


@dataclass
class Player:
    name: str = "Adventurer"
    room: str = "Town Square"
