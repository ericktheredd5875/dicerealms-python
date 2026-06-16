"""Rich UI display for the DiceRealms client."""

from rich.console import Console
from rich.panel import Panel


class ClientUI:
    def __init__(self) -> None:
        self.console = Console()


    def display(self, message: dict) -> None:
        """Display a message in the console."""
        handlers = {
            "welcome": self.display_welcome,
            "connected": self.display_connected,
            "player_joined": self.display_player_joined,
            "player_left": self.display_player_left,
            "chat": self.display_chat,
            "action_announcement": self.display_action_announcement,
            "action_result": self.display_action_result,
            "turn_status": self.display_turn_status,
            "error": self.display_error,
        }

        handler = handlers.get(message.get("type", ""))
        if handler:
            handler(message)
        else:
            self.console.print(f"[dim]{message}[/dim]")


    def display_welcome(self, message: dict) -> None:
        self.console.print(
            Panel(
                f"[bold cyan]{message.get('message', '')}[/bold cyan]\n"
                f"Player ID: [dim]{message.get('player_id', 'N/A')}[/dim]",
                title="[bold green]Welcome[/bold green]",
                border_style="green",
            )
        )


    def display_connected(self, message: dict) -> None:
        self.console.print(
            Panel(
                f"[bold green]{message.get('message', '')}[/bold green]",
                title=f"[bold]Connected as {message.get('player_name', 'Unknown')}[/bold]",
                border_style="green",
            )
        )
        

    def display_player_joined(self, message: dict) -> None:
        self.console.print(
            f"[dim]→[/dim] [cyan]{message.get('player', 'Someone')}[/cyan] joined the game"
        )


    def display_player_left(self, message: dict) -> None:
        self.console.print(
            f"[dim]←[/dim] [yellow]{message.get('player', 'Someone')}[/yellow] left the game"
        )


    def display_chat(self, message: dict) -> None:
        self.console.print(
            f"[bold cyan]{message.get('player', 'Unknown')}[/bold cyan]: "
            f"{message.get('message', '')}"
        )


    def display_action_announcement(self, message: dict) -> None:
        self.console.print(
            Panel(
                f"[bold]{message.get('player')}[/bold] is about to [cyan]{message.get('action')}[/cyan] {message.get('args', '')}",
                title="[bold yellow]Action Incoming[/bold yellow]",
                border_style="yellow",
            )
        )



    def display_action_result(self, message: dict) -> None:
        self.console.print(
            Panel(
                f"[bold]Player:[/bold] {message.get('player', 'Unknown')}\n"
                f"[bold]Action:[/bold] {message.get('action', 'N/A')}\n"
                f"[bold]Result:[/bold] {message.get('result', 'N/A')}",
                title="[bold yellow]Action Result[/bold yellow]",
                border_style="yellow",
            )
        )


    def display_turn_status(self, message: dict) -> None:
        if message.get("is_your_turn"):
            self.console.print("[bold green]It's your turn![/bold green]")
        else:
            self.console.print(f"[dim]Waiting for {message.get('waiting_for', 'other player')}...[/dim]")


    def display_error(self, message: dict) -> None:
        self.console.print(
            Panel(
                f"[bold red]{message.get('message', 'Unknown error')}[/bold red]",
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
        )
