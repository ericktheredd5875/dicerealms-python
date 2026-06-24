"""Handles user input for the DiceRealms client."""

from collections.abc import Awaitable, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from dicerealms.commands import COMMAND_ALIASES, DIRECTION_ALIASES


class InputHandler:
    def __init__(self, 
        player_name: str, 
        send: Callable[[dict], Awaitable[None]]) -> None:
        self.player_name = player_name
        self.send = send
        self.console = Console(force_terminal=True)
        

    async def run(self) -> None: # the prompt loop
        self.console.print(
            "[bold]Commands:[/bold] chat <msg>, roll <dice>, move <dir>, "
            "look, stats, help, quit\n"
            "[dim]Shortcuts: n/s/e/w, l=look, q=quit, h=help[/dim]"
        )
        session = PromptSession()
        with patch_stdout(raw=True):
            while True:
                try:
                    command = await session.prompt_async(f"{self.player_name}» ")
                    if not await self._handle_command(command.strip()):
                        break
                except (EOFError, KeyboardInterrupt):
                    break
                    


    async def _handle_command(self, command: str) -> bool: # False = quit
        """Parse and dispatch a command. Returns False to quit."""
        if not command:
            return True
        
        parts = command.split()
        cmd = parts[0].lower()

        # Direction Aliases
        resolved = DIRECTION_ALIASES.get(cmd)
        if resolved or cmd in DIRECTION_ALIASES.values():
            await self.send({
                "type": "action",
                "action": "move", 
                "args": [resolved or cmd]
            })

        # Command Aliases
        cmd = COMMAND_ALIASES.get(cmd, cmd)

        if cmd == "quit":
            return False
        elif cmd == "chat":
            await self.send({"type": "chat", "message": " ".join(parts[1:])})
        elif cmd == "roll":
            dice = parts[1] if len(parts) > 1 else "1d6"
            await self.send({"type": "action", "action": "roll", "args": [dice]})
        elif cmd == "move":
            direction = parts[1] if len(parts) > 1 else ""
            await self.send({"type": "action", "action": "move", "args": [direction]})
        elif cmd == "look":
            await self.send({"type": "action", "action": "look", "args": []})
        elif cmd == "help":
            await self.send({"type": "action", "action": "help", "args": []})
        else:
            self.console.print(f"[yellow]Unknown command: {cmd}[/yellow]")

        return True

