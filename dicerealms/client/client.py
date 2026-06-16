"""Websocket client for DiceRealms"""

import asyncio
import json

import websockets
from loguru import logger

from dicerealms.client.input_handler import InputHandler
from dicerealms.client.ui import ClientUI


class GameClient:
    def __init__(self, uri: str, player_name: str) -> None:
        self.uri = uri
        self.player_name = player_name
        self.ui = ClientUI()
        self._ws: websockets.WebSocketClientProtocol | None = None
        self.connected = False


    async def connect(self) -> None:
        """Establish a websocket connection to the server."""
        self._ws = await websockets.connect(self.uri)
        self.connected = True
        logger.info(f"Connected to server at {self.uri}")
        await self.send_message({"type": "connect", "player_name": self.player_name})


    async def disconnect(self) -> None:
        """Close the websocket connection."""
        self.connected = False
        if self._ws:
            await self._ws.close()
            logger.info("Disconnected from server")


    async def send_message(self, message: dict) -> None:
        """Send a JSON message to the server."""
        if not self._ws:
            raise RuntimeError("WebSocket connection is not established.")
        await self._ws.send(json.dumps(message))


    async def _receive_loop(self) -> None:
        """Continuously receive message from the server and display them."""
        if not self._ws:
            return
        try:
            async for raw in self._ws:
                self.ui.display(json.loads(raw))
        except websockets.exceptions.ConnectionClosed:
            self.ui.console.print("[yellow]⚠️ Connection closed by server[/yellow]")
            self.connected = False


    async def run(self) -> None: 
        """Connect, then run receive + input concurrently"""
        await self.connect()
        receive_task = asyncio.create_task(self._receive_loop())
        try:
            await InputHandler(self.player_name, self.send_message).run()
        finally:
            receive_task.cancel()
            await self.disconnect()
    