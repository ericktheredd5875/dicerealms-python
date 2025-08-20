import typer

from dicerealms.core import roll_dice

app = typer.Typer(help="YourProject CLI - a magical command line tool ✨")


@app.command()
def hello(name: str = typer.Argument(..., help="Name of the person to greet")):
    """Say hello to someone"""
    typer.echo(f"Hello {name}!")


@app.command()
def roll(dice: str = typer.Argument("1d6", help="Dice roll format (e.g. 2d8)")):
    """Roll some dice, e.g. 2d6 or 1d20"""
    result = roll_dice(dice)
    typer.echo(f"You rolled {dice} → {result}")


if __name__ == "__main__":
    app()
