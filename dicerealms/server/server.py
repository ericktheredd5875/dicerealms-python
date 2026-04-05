"""
Websocket server for DiceRealms.
"""

from __future__ import annotations

import asyncio
import json

import websockets
from loguru import logger
from websockets import ServerConnection

from dicerealms.server.action_processor import ActionProcessor
from dicerealms.server.game_state import GameState

#from dicerealms.protocol.messages import ActionMessage, ChatMessage, ConnectMessage
from dicerealms.server.turn_manager import TurnManager


class GameServer:
    """
    Main game server for multiplayer DiceRealms.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host  = host
        self.port = port
        self.connected_clients: dict[str, ServerConnection] = {}
        self.player_names: dict[str, str] = {}
        self._next_player_id = 1

        # Initialize game systems
        self.turn_manager = TurnManager()
        self.game_state = GameState()

        # Initialize action processor with broadcast callback
        self.action_processor = ActionProcessor(
            game_state = self.game_state,
            turn_manager = self.turn_manager,
            broadcast_callback = self.broadcast,
        )

    async def handle_client(self, websocket: ServerConnection, path: str | None = None):
        """
        Handle a new client connection.
        """
        player_id = f"player_{self._next_player_id}"
        self._next_player_id += 1

        self.connected_clients[player_id] = websocket
        self.turn_manager.add_player(player_id)
        logger.info(f"Client connected: {player_id}")

        try:
            # Send welcome message
            await self.send_to_client(player_id, {
                "type": "welcome",
                "player_id": player_id,
                "message": "Welcome to DiceRealms! Send a 'connect' message to join the game."
            })

            # Listen for messages
            async for message in websocket:
                await self.handle_message(player_id, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {player_id}")
            self.turn_manager.remove_player(player_id)

        finally:
            # Clean-up
            if player_id in self.connected_clients:
                del self.connected_clients[player_id]
            if player_id in self.player_names:
                name = self.player_names[player_id]
                del self.player_names[player_id]
                await self.broadcast({
                    "type": "player_left",
                    "player": name,
                })

            # Remove from turn manager and game state
            self.turn_manager.remove_player(player_id)
            if self.game_state.get_player(player_id):
                self.game_state.remove_player(player_id)

    async def handle_message(self, player_id: str, raw_message: str):
        """
        Route incoming messages to the appropriate handlers.
        """
        try:
            message = json.loads(raw_message)
            msg_type = message.get("type")

            if msg_type == "connect":
                await self.handle_connect(player_id, message)
            elif msg_type == "action":
                await self.handle_action(player_id, message)
            elif msg_type == "chat":
                await self.handle_chat(player_id, message)
            else:
                await self.send_to_client(player_id, {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}"
                })

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {player_id}")
            await self.send_to_client(player_id, {
                "type": "error",
                "message": "Invalid JSON message"
            })
        
        except Exception as e:
            logger.error(f"Error handling message from {player_id}: {e}")
            await self.send_to_client(player_id, {
                "type": "error",
                "message": f"Server error: {e}"
            })

    async def handle_connect(self, player_id: str, message: dict):
        """
        Handle player connection/name setting.
        """
        player_name = message.get("player_name")
        if not player_name:
            await self.send_to_client(player_id, {
                "type": "error",
                "message": "Player name is required."
            })
            return

        self.player_names[player_id] = player_name

        # Add player to game state
        self.game_state.add_player(player_id, player_name)

        # Broadcasst player joined message to all clients
        await self.broadcast({
            "type": "player_joined",
            "player": player_name,
        })

        # Send confirmation message to player
        await self.send_to_client(player_id, {
            "type": "connected",
            "player_name": player_name,
            "message": f"Welcome, {player_name}"
        })

        # Broadcast initial turn status
        await self.broadcast_turn_status()

    async def handle_action(self, player_id: str, message: dict):
        """
        Handle game actions - Placeholder for now.
        """
        # player_name = self.player_names.get(player_id, "Unknown")
        action = message.get("action")
        args = message.get("args", [])

        if not action:
            await self.send_to_client(player_id, {
                "type": "error",
                "message": "Action is required."
            })
            return

        # Process the action (includes turn validation, announcement, execution, result)
        result = await self.action_processor.process_action(player_id, action, args)

        # if there was an error, send it to the player
        if not result.get("success"):
            await self.send_to_client(player_id, {
                "type": "error",
                "message": result.get("error", "An unknown error occurred.")
            })

        # Broadcast turn status update after action completes
        await self._broadcast_turn_status()

    async def handle_chat(self, player_id: str, message: dict):
        """
        Handle chat messages.
        """
        player = self.game_state.get_player(player_id)
        if not player:
            player_name = self.player_names.get(player_id, "Unknown")
        else:
            player_name = player.name

        chat_message = message.get("message", "")

        await self.broadcast({
            "type": "chat",
            "player": player_name,
            "message": chat_message,
        })

    async def _broadcast_turn_status(self):
        """
        Broadcast turn status to all players.
        """
        current_player_id = self.turn_manager.get_current_player()
        current_player_name = "None"

        if current_player_id:
            player = self.game_state.get_player(current_player_id)
            if player:
                current_player_name = player.name

        # Send turn status to all connected clients
        for player_id, player in self.game_state.players.items():
            turn_status = self.turn_manager.get_turn_status(player_id)
            await self.send_to_client(player_id, {
                "type": "turn_status",
                "current_player": current_player_name,
                "current_player_id": current_player_id,
                "is_your_turn": turn_status["is_your_turn"],
                "waiting_for": current_player_name if not turn_status["is_your_turn"] else None,
                "queue_position": turn_status["queue_position"],
                "queue_size": turn_status["queue_size"],
            })

    async def send_to_client(self, player_id: str, message: dict):
        """
        Send message to a specific client.
        """
        if player_id in self.connected_clients:
            try:
                await self.connected_clients[player_id].send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                logger.warning(f"Failed to send to {player_id}: connection closed")

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.
        """
        disconnected = []
        for player_id, websocket in self.connected_clients.items():
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(player_id)

        # Clean-up disconnected clients
        for player_id in disconnected:
            if player_id in self.connected_clients:
                del self.connected_clients[player_id]
            if player_id in self.player_names:
                del self.player_names[player_id]
            self.turn_manager.remove_player(player_id)
            if self.game_state.get_player(player_id):
                self.game_state.remove_player(player_id)

    async def run(self):
        """
        Start the Websocket Server.
        """
        logger.info(f"Starting DiceRealms server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future() # Run forever