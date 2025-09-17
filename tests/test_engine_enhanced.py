# tests/test_engine_enhanced.py
# SPDX-License-Identifier: MIT

from unittest.mock import Mock, patch

import pytest

from dicerealms.engine import Command, GameEngine


def test_command_creation():
    """Test Command dataclass creation."""
    handler = Mock()
    cmd = Command(name="test", help="Test command", handler=handler)

    assert cmd.name == "test"
    assert cmd.help == "Test command"
    assert cmd.handler == handler


def test_game_engine_initialization():
    """Test GameEngine initialization."""
    engine = GameEngine()

    assert not engine._running
    assert engine._input is not None
    assert engine._output is not None
    assert len(engine._commands) == 4
    assert "help" in engine._commands
    assert "roll" in engine._commands
    assert "look" in engine._commands
    assert "quit" in engine._commands


def test_game_engine_initialization_with_callbacks():
    """Test GameEngine initialization with custom callbacks."""
    input_fn = Mock(return_value="test input")
    output_fn = Mock()

    engine = GameEngine(input_fn=input_fn, output_fn=output_fn)

    assert engine._input == input_fn
    assert engine._output == output_fn


def test_game_engine_handle_empty_line():
    """Test handling empty input lines."""
    engine = GameEngine()
    result = engine.handle("")
    assert result == ""


def test_game_engine_handle_whitespace_only():
    """Test handling whitespace-only input."""
    engine = GameEngine()
    result = engine.handle("   ")
    assert result == ""


def test_game_engine_handle_help_command():
    """Test help command handling."""
    engine = GameEngine()
    result = engine.handle("help")

    assert "Commands:" in result
    assert "help" in result
    assert "roll" in result
    assert "look" in result
    assert "quit" in result


def test_game_engine_handle_roll_command():
    """Test roll command handling."""
    with patch("dicerealms.engine.roll_dice", return_value=(12, [4, 3, 5])):
        engine = GameEngine()
        result = engine.handle("roll 3d6")

        assert "3d6 -> 12 (Parts: [4, 3, 5])" in result


def test_game_engine_handle_roll_command_no_args():
    """Test roll command with no arguments."""
    engine = GameEngine()
    result = engine.handle("roll")

    assert "Usage: roll <dice-expr>" in result


def test_game_engine_handle_look_command():
    """Test look command handling."""
    engine = GameEngine()
    result = engine.handle("look")

    assert "dark room" in result
    assert "table" in result
    assert "Exits:" in result


def test_game_engine_handle_quit_command():
    """Test quit command handling."""
    engine = GameEngine()
    result = engine.handle("quit")

    assert result == "__QUIT__"
    assert not engine._running


def test_game_engine_handle_unknown_command():
    """Test handling unknown commands."""
    engine = GameEngine()
    result = engine.handle("unknown")

    assert "Unknown command: unknown" in result
    assert "try 'help'" in result


def test_game_engine_handle_case_insensitive():
    """Test that commands are case insensitive."""
    engine = GameEngine()

    result1 = engine.handle("HELP")
    result2 = engine.handle("Help")
    result3 = engine.handle("help")

    assert result1 == result2 == result3


def test_game_engine_handle_roll_error():
    """Test roll command error handling."""
    with patch("dicerealms.engine.roll_dice", side_effect=ValueError("Invalid dice")):
        engine = GameEngine()
        result = engine.handle("roll invalid")

        assert "Error: Invalid dice" in result


def test_game_engine_run_with_mock_callbacks():
    """Test the run method with mocked callbacks."""
    inputs = ["help", "roll 1d6", "quit"]
    input_iter = iter(inputs)
    outputs = []

    def input_fn():
        return next(input_iter)

    def output_fn(text):
        outputs.append(text)

    with patch("dicerealms.engine.roll_dice", return_value=(4, [4])):
        engine = GameEngine(input_fn=input_fn, output_fn=output_fn)
        engine.run()

    # Check that we got the expected outputs
    assert any("Entering DiceRealms" in output for output in outputs)
    assert any("Commands:" in output for output in outputs)
    assert any("1d6 -> 4" in output for output in outputs)
    assert any("Goodbye" in output for output in outputs)


def test_game_engine_run_handles_exceptions():
    """Test that run method handles exceptions gracefully."""
    inputs = ["invalid_command", "quit"]
    input_iter = iter(inputs)
    outputs = []

    def input_fn():
        return next(input_iter)

    def output_fn(text):
        outputs.append(text)

    engine = GameEngine(input_fn=input_fn, output_fn=output_fn)
    engine.run()

    # Should handle unknown command and continue
    assert any("Unknown command" in output for output in outputs)
    assert any("Goodbye" in output for output in outputs)


def test_game_engine_run_ignores_empty_input():
    """Test that run method ignores empty input."""
    inputs = ["", "   ", "help", "quit"]
    input_iter = iter(inputs)
    outputs = []

    def input_fn():
        return next(input_iter)

    def output_fn(text):
        outputs.append(text)

    engine = GameEngine(input_fn=input_fn, output_fn=output_fn)
    engine.run()

    # Should process help and quit, ignoring empty lines
    assert any("Commands:" in output for output in outputs)
    assert any("Goodbye" in output for output in outputs)


def test_cmd_help_formatting():
    """Test that help command formats correctly."""
    engine = GameEngine()
    result = engine._cmd_help([])

    lines = result.split("\n")
    assert lines[0] == "Commands:"

    # Check that each command is formatted with proper spacing
    for line in lines[1:]:
        if line.strip():  # Skip empty lines
            parts = line.split()
            assert len(parts) >= 2  # Should have command name and help text


def test_cmd_roll_with_modifier():
    """Test roll command with modifier."""
    with patch("dicerealms.engine.roll_dice", return_value=(15, [4, 3, 5])):
        engine = GameEngine()
        result = engine._cmd_roll(["3d6+3"])

        assert "3d6+3 -> 15 (Parts: [4, 3, 5])" in result


def test_cmd_roll_with_negative_modifier():
    """Test roll command with negative modifier."""
    with patch("dicerealms.engine.roll_dice", return_value=(9, [4, 3, 5])):
        engine = GameEngine()
        result = engine._cmd_roll(["3d6-3"])

        assert "3d6-3 -> 9 (Parts: [4, 3, 5])" in result


def test_cmd_look_returns_placeholder():
    """Test that look command returns placeholder text."""
    engine = GameEngine()
    result = engine._cmd_look([])

    assert "dark room" in result
    assert "table" in result
    assert "map" in result
    assert "Exits:" in result


def test_cmd_quit_stops_engine():
    """Test that quit command stops the engine."""
    engine = GameEngine()
    result = engine._cmd_quit([])

    assert result == "👋 Goodbye!"
    assert not engine._running
