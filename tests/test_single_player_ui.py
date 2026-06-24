"""Tests for SinglePlayerUI Rich display layer."""
from unittest.mock import patch

import pytest

from dicerealms.ui.single_player_ui import SinglePlayerUI


@pytest.fixture
def ui():
    return SinglePlayerUI()


# --- dispatch ---

@pytest.mark.parametrize("result_type,handler", [
    ("look",  "_render_look"),
    ("move",  "_render_move"),
    ("roll",  "_render_roll"),
    ("stats", "_render_stats"),
    ("help",  "_render_help"),
])
def test_render_dispatches_to_handler(ui, result_type, handler):
    with patch.object(ui, handler, return_value="") as mock:
        ui.render({"type": result_type})
        mock.assert_called_once()


def test_render_unknown_type_returns_empty(ui):
    assert ui.render({"type": "unknown_xyz"}) == ""


def test_render_error_contains_message(ui):
    result = ui.render({"type": "error", "message": "Something went wrong"})
    assert "Something went wrong" in result


def test_render_quit_contains_message(ui):
    result = ui.render({"type": "quit", "message": "👋 Goodbye!"})
    assert "Goodbye!" in result


def test_render_quit_default_message(ui):
    result = ui.render({"type": "quit"})
    assert "Goodbye!" in result


# --- look ---

@pytest.fixture
def look_result():
    return {"room": "Town Square", "description": "A busy place.", "exits": ["north", "south"]}


def test_render_look_contains_room(ui, look_result):
    assert "Town Square" in ui._render_look(look_result)


def test_render_look_contains_description(ui, look_result):
    assert "A busy place." in ui._render_look(look_result)


def test_render_look_contains_exits(ui, look_result):
    result = ui._render_look(look_result)
    assert "north" in result
    assert "south" in result


# --- move ---

@pytest.fixture
def move_result():
    return {"message": "You move south.", "room": "Tavern", "description": "Warm.", "exits": ["north"]}


def test_render_move_contains_message(ui, move_result):
    assert "You move south." in ui._render_move(move_result)


def test_render_move_contains_room(ui, move_result):
    assert "Tavern" in ui._render_move(move_result)


# --- roll ---

@pytest.fixture
def roll_result():
    return {"expression": "2d6", "total": 7, "parts": [3, 4]}


def test_render_roll_contains_expression(ui, roll_result):
    assert "2d6" in ui._render_roll(roll_result)


def test_render_roll_contains_total(ui, roll_result):
    assert "7" in ui._render_roll(roll_result)


# --- stats ---

@pytest.fixture
def stats_result():
    return {"name": "Alice", "level": 1, "xp": 0, "hp": 20, "max_hp": 20, "mp": 10, "max_mp": 10}


def test_render_stats_contains_name(ui, stats_result):
    assert "Alice" in ui._render_stats(stats_result)


def test_render_stats_contains_hp(ui, stats_result):
    assert "20/20" in ui._render_stats(stats_result)


def test_render_stats_contains_mp(ui, stats_result):
    assert "10/10" in ui._render_stats(stats_result)


# --- help ---

@pytest.fixture
def help_result():
    return {"commands": [{"name": "roll", "help": "Roll dice"}, {"name": "look", "help": "Look around"}]}


def test_render_help_contains_command_names(ui, help_result):
    result = ui._render_help(help_result)
    assert "roll" in result
    assert "look" in result


def test_render_help_contains_help_text(ui, help_result):
    assert "Roll dice" in ui._render_help(help_result)
