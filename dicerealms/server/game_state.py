"""
Manages shared game state for DiceRealms.
"""

from dataclasses import dataclass, field

from loguru import logger


@dataclass
class PlayerState:
    """State for a single player in the game."""
    player_id: str
    name: str
    room: str = "Town Square"
    # TODO: stats, inventory, etc.

@dataclass
class Room:
    """Represnts a game room in the world."""
    room_id: str
    name: str
    description: str
    exits: dict[str, str] = field(default_factory=dict) # * Direction -> room_name

class GameState:
    """
    Manages shared game state for DiceRealms.
    """

    def __init__(self):
        self.players: dict[str, PlayerState] = {}
        self.rooms: dict[str, Room] = {}
        self._initialize_world()

    def _initialize_world(self):
        """
        Initialize the game world with starting rooms.
        """
        self.rooms["Town Square"] = Room(
            name="Town Square",
            description="A bustling town square with a fountain in the center.",
            exits={"north": "Market", "east": "Tavern"}
        )
        self.rooms["Market"] = Room(
            name="Market",
            description="A busy marketplace with various stalls.",
            exits={"south": "Town Square"}
        )
        self.rooms["Tavern"] = Room(
            name="Tavern",
            description="A cozy tavern with a warm fireplace.",
            exits={"west": "Town Square"}
        )

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

        current_room = self.rooms.get(player.room)
        if not current_room:
            return False, "Room not found."

        target_room = current_room.exits.get(direction.lower())
        if not target_room:
            return False, f"No exit {direction} from {player.room}."

        if target_room not in self.rooms:
            return False, f"Target room {target_room} not found."

        player.room = target_room
        return True, f"Moved {direction} to {target_room}."

    def get_room(self, room_name: str) -> Room | None:
        """
        Get room by name.
        """
        return self.rooms.get(room_name)