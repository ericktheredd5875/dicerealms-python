# SPDX-License-Identifier: MIT
from dicerealms.player import Player


class Engine:
    def __init__(self, player: Player | None = None):
        self.player = player or Player()

    def handle(self, line: str) -> str:
        cmd = line.strip()
        if not cmd:
            return ""

        parts = cmd.split(maxsplit=1)
        verb = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if verb in {"quit", "exit"}:
            return "__QUIT__"

        if verb == "look":
            return (
                f"You are in {self.player.room}. You see a fountain and a notice board."
            )

        if verb == "say":
            text = arg or "(you say nothing)"
            return f'You say: "{text}"'

        if verb == "help":
            return "Commands: look, say <words>, help, quit"

        return f"I don't understand '{cmd}'. Try 'help'."
