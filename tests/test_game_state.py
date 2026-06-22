# SPDX-License-Identifier: MIT
"""Tests for GameState class."""


from dicerealms.server.game_state import GameState, PlayerState


class TestPlayerState:
    """Test suite for PlayerState dataclass."""

    def test_player_state_creation(self):
        """Test creating a PlayerState."""
        player = PlayerState(player_id="p1", name="Alice")
        assert player.player_id == "p1"
        assert player.name == "Alice"
        assert player.room == "town_square"  # Default

    def test_player_state_custom_room(self):
        """Test PlayerState with custom room."""
        player = PlayerState(player_id="p1", name="Alice", room="tavern")
        assert player.room == "tavern"

    def test_player_state_default_stats(self):
        player = PlayerState(player_id="p1", name="Alice")
        assert player.hp == 20
        assert player.max_hp == 20
        assert player.mp == 10
        assert player.max_hp == 20
        assert player.level == 1
        assert player.xp == 0


class TestGameState:
    """Test suite for GameState."""

    def test_initialization(self):
        """Test GameState initializes with default world."""
        gs = GameState()
        assert len(gs.players) == 0
        assert gs.world.has_room("town_square")
        assert gs.world.has_room("tavern")
        assert gs.world.has_room("market")

    def test_add_player(self):
        """Test adding a player to game state."""
        gs = GameState()
        player = gs.add_player("player_1", "Alice")
        
        assert player.player_id == "player_1"
        assert player.name == "Alice"
        assert "player_1" in gs.players
        assert gs.players["player_1"] == player

    def test_remove_player(self):
        """Test removing a player from game state."""
        gs = GameState()
        gs.add_player("player_1", "Alice")
        
        gs.remove_player("player_1")
        assert "player_1" not in gs.players

    def test_remove_nonexistent_player(self):
        """Test removing non-existent player doesn't raise error."""
        gs = GameState()
        gs.remove_player("nonexistent")  # Should not raise

    def test_get_player(self):
        """Test getting a player by ID."""
        gs = GameState()
        gs.add_player("player_1", "Alice")
        
        player = gs.get_player("player_1")
        assert player is not None
        assert player.name == "Alice"

    def test_get_player_nonexistent(self):
        """Test getting non-existent player returns None."""
        gs = GameState()
        assert gs.get_player("nonexistent") is None

    def test_get_players_in_room(self):
        """Test getting all players in a room."""
        gs = GameState()
        gs.add_player("player_1", "Alice")
        gs.add_player("player_2", "Bob")
        
        # Both start in Town Square
        players = gs.get_players_in_room("town_square")
        assert len(players) == 2
        assert all(p.room == "town_square" for p in players)

    def test_get_players_in_room_empty(self):
        """Test getting players in empty room."""
        gs = GameState()
        players = gs.get_players_in_room("market")
        assert players == []

    def test_move_player_success(self):
        """Test successfully moving a player."""
        gs = GameState()
        gs.add_player("player_1", "Alice")
        
        success, message = gs.move_player("player_1", "north")
        assert success is True
        assert gs.get_player("player_1").room == "north_road"
        assert "North Road" in message

    def test_move_player_invalid_direction(self):
        """Test moving player in invalid direction."""
        gs = GameState()
        gs.add_player("player_1", "Alice")
        
        success, message = gs.move_player("player_1", "west")
        assert success is False
        assert gs.get_player("player_1").room == "town_square"  # Unchanged
        assert "west" in message.lower() or "no exit" in message.lower()

    def test_move_player_nonexistent(self):
        """Test moving non-existent player."""
        gs = GameState()
        success, message = gs.move_player("nonexistent", "north")
        assert success is False
        assert "not found" in message.lower()

    def test_get_room(self):
        """Test getting a room by name."""
        gs = GameState()
        room = gs.get_room("town_square")
        assert room is not None
        assert room.name == "Town Square"

    def test_get_room_nonexistent(self):
        """Test getting non-existent room returns None."""
        gs = GameState()
        assert gs.get_room("Nonexistent Room") is None