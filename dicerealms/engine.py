# SPDX-License-Identifier: MIT
# dicerealms/engine.py
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from dicerealms.commands import COMMAND_ALIASES, DIRECTION_ALIASES
from dicerealms.core import roll_dice
from dicerealms.player import Player
from dicerealms.world import World


def _render_plain(result: dict) -> str:
    t = result.get("type", "")
    if t == "look":
        exits = ", ".join(result.get("exits", []))
        return (
            f"{result['room']}\n\n" 
            f"{result['description']}\n\n"
            f"Exits: {exits}"
        )
    elif t == "move":
        exits = ", ".join(result.get("exits", []))
        return (
            f"{result['message']}\n\n"
            f"{result['room']}\n\n"
            f"{result['description']}\n\n"
            f"Exits: {exits}"
        )
    elif t == "roll":
        return (
            f"{result['expression']} --> "
            f"{result['total']} "
            f"(Parts: {result['parts']})"
        )
    elif t == "stats":
        return (
            f"Name:  {result['name']}\n"
            f"Level: {result['level']} XP: {result['xp']}\n"
            f"HP:    {result['hp']}/{result['max_hp']}"
            f"MP:    {result['mp']}/{result['max_mp']}"
        )
    elif t == "help":
        rows = [f"{c['name']:<8} {c['help']}" for c in result["commands"]]
        return "Commands: \n" + "\n".join(rows)
    elif t in ("error", "quit", "empty"):
        return result.get("message", "")
    return str(result)

@dataclass
class Command:
    name: str
    help: str
    handler: Callable[[list[str]], dict]


class GameEngine:
    """
    A minimal, synchronous REPL-like game engine.
    Commands:
        - help
        - roll <dice>
        - look
        - quit
    """

    def __init__(
        self,
        input_fn: Callable[[], str] | None = None,
        output_fn: Callable[[str], None] | None = None,
        world: World | None = None,
        player: Player | None = None,
    ):
        self._running = False
        self._input = input_fn or (lambda: input("> "))
        self._output = output_fn or print
        self._world = world
        self._player = player
        self._commands: dict[str, Command] = {
            "help": Command("help", "Show Command List", self._cmd_help),
            "roll": Command("roll", "Roll dice: roll 2d6+1", self._cmd_roll),
            "look": Command("look", "Look around the current room", self._cmd_look),
            "move": Command("move", "Move in a direction: move north", self._cmd_move),
            "quit": Command("quit", "Quit the game", self._cmd_quit),
            "stats": Command("stats", "Show your character stats", self._cmd_stats),
        }


    def run(self):
        self._running = True
        self._output(
            "🎲 Entering DiceRealms. Type 'help' "
            "for commands; 'quit' to exit."
        )
        while self._running:
            raw = self._input().strip()
            if not raw:
                continue

            result = self.handle(raw)
            if result["type"] != "empty":
                self._output(_render_plain(result))


    def handle(self, line: str) -> dict:
        """Handle a single command line and return the response."""
        if not line.strip():
            return {"type": "empty"}
        parts = line.split()
        cmd, args = parts[0].lower(), parts[1:]

        # Bare direction: "n", "north", "s", "south", etc.
        resolved_dir = DIRECTION_ALIASES.get(cmd)
        if resolved_dir or cmd in DIRECTION_ALIASES.values():
            return self._cmd_move([resolved_dir or cmd])

        # Command aliases: "l" -> "look", "q" -> "quit", etc.
        cmd = COMMAND_ALIASES.get(cmd, cmd)
        command = self._commands.get(cmd)
        if command:
            try:
                result = command.handler(args)
                return result
            except Exception as e:
                return {"type": "error", "message": f"⚠️  Error: {e}"}
        return {
            "type": "error", 
            "message": f"Unknown command: {cmd} (try 'help')"
        }


    # ---- command handlers ----
    def _cmd_help(self, _: list[str]) -> dict:
        return {
            "type": "help",
            "commands": [{"name": c.name, "help": c.help} for c in self._commands.values()],
        }


    def _cmd_roll(self, args: list[str]) -> dict:
        if not args:
            return {
                "type": "error",
                "message": "Usage: roll <dice-expr> (e.g. 2d6+1)"
            }

        total, parts = roll_dice(args[0])
        return {
            "type": "roll",
            "expression": args[0],
            "total": total,
            "parts": parts
        }


    def _cmd_look(self, _: list[str]) -> dict:
        if self._world and self._player:
            room = self._world.current_room(self._player.room)
            if room:
                return {
                    "type": "look",
                    "room": room.name,
                    "description": room.description,
                    "exits": sorted(room.neighbor().keys()),
                }
        
        return {
            "type": "look",
            "room": "Dark Room",
            "description": "You are in a dark room. There is a table with a map on it.",
            "exits": ["east", "north"],
        }


    def _cmd_quit(self, _: list[str]) -> dict:
        self._running = False
        return {
            "type": "quit",
            "message": "👋 Goodbye!"
        }


    def _cmd_move(self, args: list[str]) -> dict:
        if not args:
            return {
                "type": "error",
                "message": "Usage: move <direction> (e.g. move north)"
            }
        if not self._world or not self._player:
            return {
                "type": "error",
                "message": "Cannot move: no world loaded"
            }
        
        direction = DIRECTION_ALIASES.get(args[0].lower(), args[0].lower())
        new_room_id, message = self._world.move(self._player.room, direction)
        if new_room_id:
            self._player.room = new_room_id
            room = self._world.current_room(new_room_id)
            return {
                "type": "move",
                "message": message,
                "room": room.name if room else new_room_id,
                "description": room.description if room else "",
                "exits": sorted(room.neighbor().keys()) if room else [],
            }

        return {"type": "error", "message": message}


    def _cmd_stats(self, _: list[str]) -> dict:
        if not self._player:
            return {
                "type": "error",
                "message": "No player loaded.",
            }
        
        p = self._player
        return {
            "type": "stats",
            "name": p.name,
            "level": p.level,
            "xp": p.xp,
            "hp": p.hp,
            "max_hp": p.max_hp,
            "mp": p.mp,
            "max_mp": p.max_mp
        }
        