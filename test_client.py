#!/usr/bin/env python3
"""
Test client for DiceRealms server.
Connects to the server and allows testing of the WebSocket connection.
"""

import asyncio
import json
import sys
from typing import Optional

import websockets
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


class TestClient:
    """Simple test client for DiceRealms server."""

    def __init__(self, uri: str, player_name: str):
        self.uri = uri
        self.player_name = player_name
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False

    async def connect(self):
        """Connect to the server."""
        try:
            console.print(f"[cyan]Connecting to {self.uri}...[/cyan]")
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            console.print("[green]✓ Connected![/green]")

            # Send connect message
            await self.send_message({
                "type": "connect",
                "player_name": self.player_name,
            })
            console.print(f"[dim]Sent connect message as '{self.player_name}'[/dim]")

        except Exception as e:
            console.print(f"[bold red]Connection failed:[/bold red] {e}")
            raise

    async def send_message(self, message: dict):
        """Send a JSON message to the server."""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        await self.websocket.send(json.dumps(message))
        logger.debug(f"Sent: {message}")

    async def receive_messages(self):
        """Receive and display messages from the server."""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            console.print("[yellow]Connection closed by server[/yellow]")
            self.connected = False
        except Exception as e:
            console.print(f"[bold red]Error receiving message:[/bold red] {e}")
            self.connected = False

    async def handle_message(self, raw_message: str):
        """Handle incoming message from server."""
        try:
            message = json.loads(raw_message)
            msg_type = message.get("type", "unknown")

            # Format and display the message
            if msg_type == "welcome":
                console.print(
                    Panel(
                        f"[bold cyan]{message.get('message', '')}[/bold cyan]\n"
                        f"Player ID: [dim]{message.get('player_id', 'N/A')}[/dim]",
                        title="[bold green]Welcome[/bold green]",
                        border_style="green",
                    )
                )

            elif msg_type == "connected":
                console.print(
                    Panel(
                        f"[bold green]{message.get('message', '')}[/bold green]",
                        title=f"[bold]Connected as {message.get('player_name', 'Unknown')}[/bold]",
                        border_style="green",
                    )
                )

            elif msg_type == "player_joined":
                console.print(
                    f"[dim]→[/dim] [cyan]{message.get('player', 'Someone')}[/cyan] joined the game"
                )

            elif msg_type == "player_left":
                console.print(
                    f"[dim]←[/dim] [yellow]{message.get('player', 'Someone')}[/yellow] left the game"
                )

            elif msg_type == "chat":
                console.print(
                    f"[bold cyan]{message.get('player', 'Unknown')}[/bold cyan]: "
                    f"{message.get('message', '')}"
                )

            elif msg_type == "action_result":
                console.print(
                    Panel(
                        f"[bold]Player:[/bold] {message.get('player', 'Unknown')}\n"
                        f"[bold]Action:[/bold] {message.get('action', 'N/A')}\n"
                        f"[bold]Result:[/bold] {message.get('result', 'N/A')}",
                        title="[bold yellow]Action Result[/bold yellow]",
                        border_style="yellow",
                    )
                )

            elif msg_type == "error":
                console.print(
                    Panel(
                        f"[bold red]{message.get('message', 'Unknown error')}[/bold red]",
                        title="[bold red]Error[/bold red]",
                        border_style="red",
                    )
                )

            else:
                console.print(f"[dim]Received:[/dim] {message}")

        except json.JSONDecodeError:
            console.print(f"[red]Invalid JSON received:[/red] {raw_message}")
        except Exception as e:
            console.print(f"[bold red]Error handling message:[/bold red] {e}")

    async def run_interactive(self):
        """Run interactive mode - send commands manually."""
        console.print(
            Panel.fit(
                "[bold cyan]Interactive Test Client[/bold cyan]\n"
                "Type commands or 'help' for options\n"
                "Type 'quit' to exit",
                border_style="cyan",
            )
        )

        # Start message receiver in background
        receive_task = asyncio.create_task(self.receive_messages())

        try:
            while self.connected:
                # Get user input (non-blocking)
                try:
                    command = await asyncio.to_thread(
                        Prompt.ask, f"[bold cyan]{self.player_name}>[/bold cyan] "
                    )

                    if not command or command.lower() == "quit":
                        break

                    if command.lower() == "help":
                        console.print(
                            "[bold]Available commands:[/bold]\n"
                            "  [cyan]chat <message>[/cyan] - Send a chat message\n"
                            "  [cyan]action <action> [args...][/cyan] - Send an action\n"
                            "  [cyan]roll <dice>[/cyan] - Roll dice (e.g., 'roll 2d6')\n"
                            "  [cyan]help[/cyan] - Show this help\n"
                            "  [cyan]quit[/cyan] - Disconnect and exit"
                        )
                        continue

                    # Parse command
                    parts = command.split()
                    if not parts:
                        continue

                    cmd = parts[0].lower()

                    if cmd == "chat":
                        message_text = " ".join(parts[1:]) if len(parts) > 1 else ""
                        await self.send_message({
                            "type": "chat",
                            "message": message_text,
                        })

                    elif cmd == "action":
                        action_name = parts[1] if len(parts) > 1 else "test"
                        action_args = parts[2:] if len(parts) > 2 else []
                        await self.send_message({
                            "type": "action",
                            "action": action_name,
                            "args": action_args,
                        })

                    elif cmd == "roll":
                        dice_expr = parts[1] if len(parts) > 1 else "1d6"
                        await self.send_message({
                            "type": "action",
                            "action": "roll",
                            "args": [dice_expr],
                        })

                    else:
                        console.print(f"[yellow]Unknown command: {cmd}[/yellow]")

                except KeyboardInterrupt:
                    break

        finally:
            receive_task.cancel()
            if self.websocket:
                await self.websocket.close()
            console.print("[yellow]Disconnected[/yellow]")

    async def run_auto_test(self):
        """Run automatic test sequence."""
        console.print(
            Panel.fit(
                "[bold cyan]Automatic Test Sequence[/bold cyan]",
                border_style="cyan",
            )
        )

        # Start message receiver in background
        receive_task = asyncio.create_task(self.receive_messages())

        try:
            # Wait a moment for welcome message
            await asyncio.sleep(1)

            # Test 1: Send chat message
            console.print("\n[bold]Test 1:[/bold] Sending chat message...")
            await self.send_message({
                "type": "chat",
                "message": "Hello from test client!",
            })
            await asyncio.sleep(1)

            # Test 2: Send action
            console.print("\n[bold]Test 2:[/bold] Sending action...")
            await self.send_message({
                "type": "action",
                "action": "roll",
                "args": ["2d6"],
            })
            await asyncio.sleep(1)

            # Test 3: Send another action
            console.print("\n[bold]Test 3:[/bold] Sending another action...")
            await self.send_message({
                "type": "action",
                "action": "look",
                "args": [],
            })
            await asyncio.sleep(1)

            console.print("\n[green]✓ All tests completed![/green]")
            console.print("[dim]Waiting 3 seconds, then disconnecting...[/dim]")
            await asyncio.sleep(3)

        finally:
            receive_task.cancel()
            if self.websocket:
                await self.websocket.close()
            console.print("[yellow]Disconnected[/yellow]")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test client for DiceRealms server")
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Server port (default: 8765)",
    )
    parser.add_argument(
        "--name",
        default="TestPlayer",
        help="Player name (default: TestPlayer)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run automatic test sequence instead of interactive mode",
    )

    args = parser.parse_args()

    uri = f"ws://{args.host}:{args.port}"

    client = TestClient(uri, args.name)

    try:
        await client.connect()

        if args.auto:
            await client.run_auto_test()
        else:
            await client.run_interactive()

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Client error")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())