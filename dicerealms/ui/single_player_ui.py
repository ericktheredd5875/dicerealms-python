# SPD-License-Identifier: MIT

class SinglePlayerUI:
    
    def render(self, result: dict) -> str:
        t = result.get("type", "")
        if t == "look":
            return self._render_look(result)
        elif t == "move":
            return self._render_move(result)
        elif t == "roll":
            return self._render_roll(result)
        elif t == "stats":
            return self._render_stats(result)
        elif t == "help":
            return self._render_help(result)
        elif t == "who":
            return self._render_who(result)
        elif t == "inspect":
            return self._render_inspect(result)
        elif t == "error":
            return f"[red]{result.get('message', '')}[/red]"
        elif t == "quit":
            return f"[yellow]{result.get('message', 'Goodbye!')}[/yellow]"
        return ""


    def _render_look(self, result: dict) -> str:
        exits = ", ".join(result.get("exits", []))
        return (
            f"[bold cyan]{result['room']}[/bold cyan]\n"
            f"{result['description']}\n\n"
            f"[dim]Exits: {exits}[/dim]"
        )
    

    def _render_move(self, result: dict) -> str:
        exits = ", ".join(result.get("exits", []))
        return (
            f"[green]{result['message']}[/green]\n\n"
            f"[bold cyan]{result['room']}[/bold cyan]\n"
            f"{result['description']}\n\n"
            f"[dim]Exits: {exits}[/dim]"
        )
    

    def _render_roll(self, result: dict) -> str:
        return (
            f"[dim]{result['expression']}[/dim] → "
            f"[bold yellow]{result['total']}[/bold yellow]  "
            f"[dim]{result['parts']}[/dim]"
        )
    

    def _render_stats(self, result: dict) -> str:
        return (
            f"[bold]{result['name']}[/bold]\n"
            f"Level [bold]{result['level']}[/bold]  •  "
            f"[dim]{result['xp']} XP[/dim]\n\n"
            f"HP  [green]{result['hp']}/{result['max_hp']}[/green]\n"
            f"MP  [blue]{result['mp']}/{result['max_mp']}[/blue]"
        )
    

    def _render_help(self, result: dict) -> str:
        rows = [
            f"  [bold cyan]{c['name']:<8}[/bold cyan] {c['help']}"
            for c in result["commands"]
        ]
        return "[bold]Commands:[/bold]\n" + "\n".join(rows)


    def _render_who(self, result: dict) -> str:
        players = result.get("players", [])
        rows = [
            f"  [cyan]{p['name']}[/cyan] [dim]({p['room']})[/dim]"
            for p in players
        ]
        return "[bold]Players in game:[/bold]\n" + "\n".join(rows)


    def _render_inspect(self, result: dict) -> str:
        return (
            f"[bold]{result['name']}[/bold]\n"
            f"Level [bold]{result['level']}[/bold]\n\n"
            f"HP  [green]{result['hp']}/{result['max_hp']}[/green]\n"
            f"MP  [blue]{result['mp']}/{result['max_mp']}[/blue]"
        )