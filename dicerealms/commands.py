# SPDX-License-Identifier: MIT
from dataclasses import dataclass

DIRECTION_ALIASES: dict[str, str] = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "u": "up",
    "d": "down",
}

COMMAND_ALIASES: dict[str, str] = {
    "l": "look",
    "q": "quit",
    "h": "help",
    "?": "help",
    "go": "move",
}


@dataclass
class CommandDef:
    name: str
    help: str
    free: bool = False          # True = no turn cost, no turn validation
    multiplayer_only: bool = False


COMMANDS: list[CommandDef] = [
    CommandDef("roll",    "Roll dice (e.g. 2d6+1)"),
    CommandDef("move",    "Move in a direction (n/s/e/w or full name)"),
    CommandDef("look",    "Get a description of the current room",       free=True),
    CommandDef("who",     "List all players in the game",                free=True),
    CommandDef("inspect", "View another player's stats: inspect <name>", free=True),
    CommandDef("stats",   "View your character stats",                   free=True),
    CommandDef("chat",    "Send a message to all players",               free=True,  multiplayer_only=True),
    CommandDef("help",    "View this help menu",                         free=True),
    CommandDef("quit",    "Quit the game"),
]

FREE_ACTIONS: frozenset[str] = frozenset(c.name for c in COMMANDS if c.free)
