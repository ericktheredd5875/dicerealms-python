# tests/test_cli.py
# SPDX-License-Identifier: MIT

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from dicerealms.cli import app, hello, new, roll, start


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_new_command(runner):
    """Test the new command."""
    result = runner.invoke(app, ["new"])
    assert result.exit_code == 0
    assert "New game created" in result.output


def test_cli_start_command(runner):
    """Test the start command."""
    # Mock the global _engine variable to ensure it starts as None
    with patch("dicerealms.cli._engine", None):
        with patch("dicerealms.cli.GameEngine") as mock_engine_class:
            mock_engine = Mock()
            mock_engine.run.return_value = None
            mock_engine_class.return_value = mock_engine

            # Mock the typer.echo calls to prevent interactive output
            with patch("typer.echo"):
                result = runner.invoke(app, ["start"], input="quit\n")
                assert result.exit_code == 0
                mock_engine_class.assert_called_once()
                mock_engine.run.assert_called_once()


def test_cli_hello_command(runner):
    """Test the hello command."""
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello World!" in result.output


def test_cli_roll_command(runner):
    """Test the roll command."""
    with patch("dicerealms.cli.roll_dice", return_value=(12, [4, 3, 5])):
        result = runner.invoke(app, ["roll", "3d6"])
        assert result.exit_code == 0
        assert "3d6 -> 12 (Parts: [4, 3, 5])" in result.output


def test_cli_roll_command_default(runner):
    """Test the roll command with default dice."""
    with patch("dicerealms.cli.roll_dice", return_value=(4, [4])):
        result = runner.invoke(app, ["roll"])
        assert result.exit_code == 0
        assert "1d6 -> 4 (Parts: [4])" in result.output


def test_cli_roll_command_invalid_dice(runner):
    """Test the roll command with invalid dice expression."""
    with patch(
        "dicerealms.cli.roll_dice", side_effect=ValueError("Invalid dice format")
    ):
        result = runner.invoke(app, ["roll", "invalid"])
        assert result.exit_code != 0


def test_new_function():
    """Test the new function directly."""
    with patch("dicerealms.cli._engine", None):
        new()
        # Should not raise any exceptions
        assert True


def test_start_function_with_existing_engine():
    """Test start function with existing engine."""
    with patch("dicerealms.cli._engine", Mock()) as mock_engine:
        with patch("typer.echo") as mock_echo:
            start()
            mock_engine.run.assert_called_once()
            mock_echo.assert_called()


def test_hello_function():
    """Test the hello function directly."""
    with patch("typer.echo") as mock_echo:
        hello("TestUser")
        mock_echo.assert_called_once_with("Hello TestUser!")


def test_roll_function():
    """Test the roll function directly."""
    with patch("dicerealms.cli.roll_dice", return_value=(15, [6, 5, 4])) as mock_roll:
        with patch("typer.echo") as mock_echo:
            roll("3d6")
            mock_roll.assert_called_once_with("3d6")
            mock_echo.assert_called_once_with("3d6 -> 15 (Parts: [6, 5, 4])")
