# tests/test_player.py
# SPDX-License-Identifier: MIT

import pytest

from dicerealms.player import Player


def test_player_default_values():
    """Test Player with default values."""
    player = Player()
    assert player.name == "Adventurer"
    assert player.room == "Town Square"


def test_player_custom_values():
    """Test Player with custom values."""
    player = Player(name="Gandalf", room="Rivendell")
    assert player.name == "Gandalf"
    assert player.room == "Rivendell"


def test_player_equality():
    """Test Player equality comparison."""
    player1 = Player(name="Aragorn", room="Minas Tirith")
    player2 = Player(name="Aragorn", room="Minas Tirith")
    player3 = Player(name="Legolas", room="Minas Tirith")

    assert player1 == player2
    assert player1 != player3


def test_player_repr():
    """Test Player string representation."""
    player = Player(name="Frodo", room="Shire")
    repr_str = repr(player)
    assert "Player" in repr_str
    assert "Frodo" in repr_str
    assert "Shire" in repr_str
