"""
Turn-based system for DiceRealms.
Manages turn order and enforces one action per turn.
"""

from loguru import logger


class TurnManager:
    """
    Manages turn order and enforces one action per turn.
    """

    def __init__(self):
        self.turn_queue: list[str] = [] # * Ordered list of player_ids
        self.current_turn_index: int = 0
        self.turn_in_progress: bool = False # * True when action is being processed

    def add_player(self, player_id: str) -> bool:
        """
        Add a player to the turn queue.
        Returns True if added, False if already in queue.
        """
        if player_id in self.turn_queue:
            logger.warning(f"[{player_id}] Player already in turn queue.")
            return False

        self.turn_queue.append(player_id)
        logger.info(f"[{player_id}] Added to turn queue. (Position: {len(self.turn_queue)})")

        # If this is the first player, they get the first turn
        if len(self.turn_queue) == 1:
            logger.info(f"[{player_id}] Current Player and first in queue..")

        return True

    def remove_player(self, player_id: str) -> bool:
        """
        Remove a player from the turn queue.
        Handles current turn adjustment if needed.
        Returns True if removed, False if not found.
        """

        if player_id not in self.turn_queue:
            logger.warning(f"[{player_id}] Player not in turn queue.")
            return False

        # Find the index of the player to remove
        removed_index = self.turn_queue.index(player_id)
        logger.info(f"[{player_id}] Removed from turn queue at index: {removed_index}")
        
        # Remove the player from the queue
        del self.turn_queue[removed_index]
        logger.info(f"[{player_id}] Removed from turn queue.")

        # Adjust current_turn_index if needed
        if not self.turn_queue:
            # No players left
            self.current_turn_index = 0
            return True

        # If we removed a player before the current turn, adjust the index
        if removed_index < self.current_turn_index:
            self.current_turn_index -= 1
        # If we removed the current player, move to next (or wrap)
        elif removed_index == self.current_turn_index:
            # Don't advance if we're at the end - just reset to 0
            if self.current_turn_index >= len(self.turn_queue):
                self.current_turn_index = 0
            # current_turn_index now points to the next player
        # if we removed a player after current, no adjustment needed

        return True

    def get_current_player(self) -> str | None:
        """
        Get the player_id whos turn it is.
        Returns None if no players are in the queue.
        """
        if not self.turn_queue:
            return None

        return self.turn_queue[self.current_turn_index]

    def is_current_turn(self, player_id: str) -> bool:
        """
        Check if it's the specific player's turn.
        """
        current_player = self.get_current_player()
        return current_player == player_id and not self.turn_in_progress

    def start_turn_action(self, player_id: str) -> bool:
        """
        Mark that a turn action has started.
        Returns True if it's the player's turn and action can start.
        Returns False if it's not the player's turn or action already in progress.
        """
        if not self.is_current_turn(player_id):
            return False

        if self.turn_in_progress:
            logger.warning(f"[{player_id}] Turn action already in progress for another player.")
            return False

        self.turn_in_progress = True
        logger.debug(f"[{player_id}] Turn action started.")
        return True

    def end_turn_action(self):
        """
        Mark that the current turn action has completed.
        This should be called after the action processing is done.
        """
        self.turn_in_progress = False
        logger.debug("Turn action completed.")

    def advance_turn(self) -> str | None:
        """
        Advance to the next player's turn.
        Returns the player_id of the new current player, or None if no players.
        """
        if not self.turn_queue:
            logger.warning("Cannot advance turn: no players in queue.")
            return None

        if self.turn_in_progress:
            logger.warning("Cannot advance turn: action in progress.")
            return None
        
        # Move to next player (with wrap-around)
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_queue)
        new_current = self.get_current_player()

        logger.info(f"Turn advanced to {new_current} (Index: {self.current_turn_index}).")
        return new_current

    def get_turn_status(self, player_id: str) -> dict:
        """
        Get turn status information for a specific player.
        Returns dict with:
            - is_your_turn: bool
            - current_player: str (player_id)
            - current_player_name: str (if provided via game_state)
            - queue_position: int (0-based index, -1 if not in queue)
            - queue_size: int
            - turn_in_progress: bool
        """
        is_your_turn = self.is_current_turn(player_id)
        current_player = self.get_current_player()

        queue_position = -1
        if player_id in self.turn_queue:
            queue_position = self.turn_queue.index(player_id)

        return {
            "is_your_turn": is_your_turn,
            "current_player": current_player,
            # "current_player_name": current_player_name,
            "queue_position": queue_position,
            "queue_size": len(self.turn_queue),
            "turn_in_progress": self.turn_in_progress
        }

    def get_turn_queue(self) -> list[str]:
        """
        Get the current turn queue (ordered list of player_ids)
        """
        return self.turn_queue.copy()

    def reset_turn_queue(self):
        """
        Reset the turn queue (useful for game resets).
        """

        self.turn_queue.clear()
        self.current_turn_index = 0
        self.turn_in_progress = False
        logger.info("Turn queue reset.")

    def get_next_player(self) -> str | None:
        """
        Get the player_id who will have the next turn (without advancing).
        Useful for displaying "Next up: Player X" messages.
        """
        if not self.turn_queue:
            return None

        next_index = (self.current_turn_index + 1) % len(self.turn_queue)
        return self.turn_queue[next_index]