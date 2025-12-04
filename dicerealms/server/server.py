"""
Websocket server for DiceRealms.
"""

import asyncio
import json

import websockets
from loguru import logger
from websockets.server import WebSocketServerProtocol

#from dicerealms.protocol.messages import ActionMessage, ChatMessage, ConnectMessage
from dicerealms.server.turn_manager import TurnManager


class GameServer:
    """
    Main game server for multiplayer DiceRealms.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host  = host
        self.port = port
        self.connected_clients: dict[str, WebSocketServerProtocol] = {}
        self.player_names: dict[str, str] = {}
        self._next_player_id = 1
        self.turn_manager = TurnManager()

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str = None):
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
            self.turn_manager.remove_player(player_id)

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
        self.player_names[player_id] = player_name

        await self.broadcast({
            "type": "player_joined",
            "player": player_name,
        })

        await self.send_to_client(player_id, {
            "type": "connected",
            "player_name": player_name,
            "message": f"Welcome, {player_name}"
        })

    async def handle_action(self, player_id: str, message: dict):
        """
        Handle game actions - Placeholder for now.
        """
        player_name = self.player_names.get(player_id, "Unknown")
        action = message.get("action")
        args = message.get("args", [])

        if not self.turn_manager.is_current_turn(player_id):
            await self.send_to_client(player_id, {
                "type": "error",
                "message": f"Not your turn! Waiting for {self.turn_manager.get_current_player()}"
            })
            return

        # Start action
        self.turn_manager.start_turn_action(player_id)

        # For now, just echo
        await self.broadcast({
            "type": "action_result",
            "player": player_name,
            "action": action,
            "result": f"Action {action} by {player_name} with args: {args}",
            "details": {}
        })

        # End action
        self.turn_manager.end_turn_action()
        next_player = self.turn_manager.get_next_player()
        if next_player:
            await self.send_to_client(next_player, {
                "type": "next_turn",
                "player": next_player,
                "message": f"It's your turn, {next_player}!"
            })
        else:
            await self.broadcast({
                "type": "no_players",
                "message": "No players left in the game."
            })

    async def handle_chat(self, player_id: str, message: dict):
        """
        Handle chat messages.
        """
        player_name = self.player_names.get(player_id, "Unknown")
        chat_message = message.get("message", "")

        await self.broadcast({
            "type": "chat",
            "player": player_name,
            "message": chat_message,
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

    async def run(self):
        """
        Start the Websocket Server.
        """
        logger.info(f"Starting DiceRealms server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future() # Run forever