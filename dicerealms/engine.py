# SPDX-License-Identifier: MIT
# dicerealms/engine.py
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from dicerealms.core import roll_dice


@dataclass
class Command:
    name: str
    help: str
    handler: Callable[[list[str]], str]


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
    ):
        self._running = False
        self._input = input_fn or (lambda: input("> "))
        self._output = output_fn or print
        self._commands: dict[str, Command] = {
            "help": Command("help", "Show Command List", self._cmd_help),
            "roll": Command("roll", "Roll dice: roll 2d6+1", self._cmd_roll),
            "look": Command("look", "Look around the current room", self._cmd_look),
            "quit": Command("quit", "Quit the game", self._cmd_quit),
        }

    def run(self):
        self._running = True
        self._output("🎲 Entering DiceRealms. Type 'help' for commands; 'quit' to exit.")
        while self._running:
            raw = self._input().strip()
            if not raw:
                continue

            parts = raw.split()
            cmd, args = parts[0].lower(), parts[1:]
            handler = self._commands.get(cmd)
            if handler:
                try:
                    msg = handler.handler(args)
                except Exception as e:  # Keep REPL alive
                    msg = f"⚠️  Error: {e}"
            else:
                msg = f"Unknown command: {cmd} (try 'help')"

            self._output(msg)

    def handle(self, line: str) -> str:
        """Handle a single command line and return the response."""
        if not line.strip():
            return ""

        parts = line.split()
        cmd, args = parts[0].lower(), parts[1:]
        handler = self._commands.get(cmd)

        if handler:
            try:
                result = handler.handler(args)
                if cmd == "quit":
                    return "__QUIT__"
                return result
            except Exception as e:
                return f"⚠️  Error: {e}"
        else:
            return f"Unknown command: {cmd} (try 'help')"

    # ---- command handlers ----
    def _cmd_help(self, _: list[str]) -> str:
        rows = [f"{c.name:<8} {c.help}" for c in self._commands.values()]
        return "Commands:\n" + "\n".join(rows)

    def _cmd_roll(self, args: list[str]) -> str:
        if not args:
            return "Usage: roll <dice-expr> (e.g. 2d6+1)"

        total, parts = roll_dice(args[0])
        return f"{args[0]} -> {total} (Parts: {parts})"

    def _cmd_look(self, _: list[str]) -> str:
        # TODO: Implement room description and connect world state
        return "You are in a dark room. There is a table with a map on it. Exits: north, east."

    def _cmd_quit(self, _: list[str]) -> str:
        self._running = False
        return "👋 Goodbye!"
