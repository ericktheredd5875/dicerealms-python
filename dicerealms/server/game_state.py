"""
Manages shared game state for DiceRealms.
"""

from dataclasses import dataclass

from loguru import logger

from dicerealms.world import World, load_default_world


@dataclass
class PlayerState:
    """State for a single player in the game."""
    player_id: str
    name: str
    room: str = "town_square"
    # TODO: stats, inventory, etc.


class GameState:
    """
    Manages shared game state for DiceRealms.
    """

    def __init__(self):
        self.players: dict[str, PlayerState] = {}
        self.world: World = load_default_world()

    def add_player(self, player_id: str, name: str) -> PlayerState:
        """
        Add a new player to the game.
        """

        player = PlayerState(player_id=player_id, name=name)
        self.players[player_id] = player
        logger.info(f"[{player_id}] Player {name} joined the game.")
        return player

    def remove_player(self, player_id: str) :
        """
        Remove a player from the game.
        """
        if player_id in self.players:
            name = self.players[player_id].name
            del self.players[player_id]
            logger.info(f"[{player_id}] Removed player {name} from the game.")

    def get_player(self, player_id: str) -> PlayerState | None:
        """
        Get player state by ID.
        """

        return self.players.get(player_id)

    def get_players_in_room(self, room_name: str) -> list[PlayerState]:
        """
        Get all players in a specific room.
        """
        return [p for p in self.players.values() if p.room == room_name]

    def move_player(self, player_id: str, direction: str) -> tuple[bool, str]:
        """
        Move player to another room. Returns (success, message).
        """
        player = self.get_player(player_id)
        if not player:
            return False, "Player not found."

        new_room_id, message = self.world.move(player.room, direction)
        if new_room_id:
            player.room = new_room_id
            return True, message
        
        return False, message

    def get_room(self, room_id: str):
        """
        Get room by ID.
        """
        return self.world.current_room(room_id)