
"""
CLI Commands for DiceRealms.
"""

import asyncio

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel

from dicerealms.server.server import GameServer

#from typing import Optional



app = typer.Typer(
    help="DiceRealms CLI -- a multiplayer, turn-based, dice-driven fantasy RPG ✨",
    add_completion = False,
)

console = Console()

@app.command()
def server(
    host: str = typer.Option("localhost", "--host", "-h",  help="Host to bind the server to."),
    port: int = typer.Option(8765, "--port", "-p", help="Port to bind the server to.")
) -> None:
    """
    Start the DiceRealms multiplayer server.

    Example:
        dicerealms server --host 0.0.0.0 --port 8765
    """

    console.print(
        Panel.fit(
            f"[bold cyan]🎲 DiceRealms Server[/bold cyan]\n"
            f"Starting on [bold]{host}:{port}[/bold]\n",
            border_style="bright_cyan",
        )
    )

    # Create and run the server
    game_server = GameServer(host=host, port=port)

    try:
        # Run the async server
        asyncio.run(game_server.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Server shutting down...[/yellow]")
        logger.info("Server stopped by user")
    except Exception as e:
        console.print(f"[bold red]❌ Server error:[/bold red] {e}")
        logger.error(f"Server error: {e}")
        raise typer.Exit(code=1)  from None
    
@app.command()
def connect(
    host: str = typer.Option("localhost", "--host", "-h",  help="Host to connect to."),
    port: int = typer.Option(8765, "--port", "-p", help="Port to connect to."),
    name: str = typer.Option("Player", "--name", "-n", help="Player name."),
) -> None:
    """
    Connect to a DiceRealms server as a client.

    Example:
        dicerealms connect --host localhost --port 8765 --name Alice
    """

    console.print(
        Panel.fit(
            f"[bold green]🎲 DiceRealms Client[/bold green]\n"
            f"Connecting to [bold]{host}:{port}[/bold]\n"
            f"Player name: [bold]{name}[/bold]\n",
            border_style="green",
        )
    )

    # TODO: implement client connection
    console.print("[yellow]🔗 Client connection not yet implemented.[/yellow]")
    console.print("[dim]Coming soon in M3![/dim]")

if __name__ == "__main__":
    app()

