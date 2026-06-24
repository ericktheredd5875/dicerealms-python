"""Tests for the enhanced command parser — aliases and direction shortcuts."""
import pytest

from dicerealms.commands import COMMAND_ALIASES, DIRECTION_ALIASES
from dicerealms.engine import GameEngine
from dicerealms.player import Player
from dicerealms.world import load_default_world

# --- constants ---

@pytest.mark.parametrize("alias,expected", [
    ("n", "north"), ("s", "south"), ("e", "east"), ("w", "west"),
    ("u", "up"), ("d", "down"),
])
def test_direction_aliases_map_correctly(alias, expected):
    assert DIRECTION_ALIASES[alias] == expected


@pytest.mark.parametrize("alias,expected", [
    ("l", "look"), ("q", "quit"), ("h", "help"), ("?", "help"), ("go", "move"),
])
def test_command_aliases_map_correctly(alias, expected):
    assert COMMAND_ALIASES[alias] == expected


# --- engine fixtures ---

@pytest.fixture
def engine():
    return GameEngine()


@pytest.fixture
def full_engine():
    return GameEngine(world=load_default_world(), player=Player())


# --- bare direction shortcuts ---

@pytest.mark.parametrize("shortcut,expected_type", [
    ("s", "move"),   # town_square -> tavern
    ("n", "move"),   # town_square -> north_road
    ("e", "error"),  # no east exit from town_square
])
def test_bare_direction_shortcuts(full_engine, shortcut, expected_type):
    result = full_engine.handle(shortcut)
    assert result["type"] == expected_type


@pytest.mark.parametrize("shortcut,expected_type", [
    ("south", "move"),
    ("north", "move"),
    ("east", "error"),
])
def test_full_direction_words_work_bare(full_engine, shortcut, expected_type):
    result = full_engine.handle(shortcut)
    assert result["type"] == expected_type


# --- direction normalization in move ---

def test_move_with_direction_alias(full_engine):
    result = full_engine.handle("move s")
    assert result["type"] == "move"
    assert "Tavern" in result["room"]


def test_move_with_full_direction(full_engine):
    result = full_engine.handle("move south")
    assert result["type"] == "move"
    assert "Tavern" in result["room"]


# --- command aliases ---

def test_l_triggers_look(full_engine):
    result = full_engine.handle("l")
    assert result["type"] == "look"


def test_q_triggers_quit(engine):
    result = engine.handle("q")
    assert result["type"] == "quit"


def test_h_triggers_help(engine):
    result = engine.handle("h")
    assert result["type"] == "help"


def test_question_mark_triggers_help(engine):
    result = engine.handle("?")
    assert result["type"] == "help"


def test_go_triggers_move(full_engine):
    result = full_engine.handle("go south")
    assert result["type"] == "move"
    assert "Tavern" in result["room"]
