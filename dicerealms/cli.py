# SPDX-License-Identifier: MIT
# dicerealms/cli.py
from __future__ import annotations

import typer

from dicerealms.core import roll_dice
from dicerealms.engine import GameEngine

app = typer.Typer(help="DiceRealms – a D&D-style, terminal-first adventure. ✨")

_engine: GameEngine | None = None


@app.command()
def new():
    """Start a fresh game session in memory."""
    global _engine
    _engine = GameEngine()
    typer.echo("🧙 New game created. Type 'start' to begin.")


@app.command()
def start():
    """Enter the interactive game loop."""
    global _engine

    if _engine is None:
        _engine = GameEngine()

    typer.echo("🎲 Entering DiceRealms. Type 'help' for commands; 'quit' to exit.")
    _engine.run()


@app.command()
def hello(name: str = typer.Argument(..., help="Name of the person to greet")):
    """Say hello to someone"""
    typer.echo(f"Hello {name}!")


@app.command()
def roll(expr: str = typer.Argument("1d6", help="Dice expression like 2d6+1")):
    """Roll some dice, e.g. 2d6 or 1d20"""
    total, parts = roll_dice(expr)
    typer.echo(f"{expr} -> {total} (Parts: {parts})")


if __name__ == "__main__":
    app()
