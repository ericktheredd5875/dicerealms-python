# SPDX-License-Identifier: MIT
"""Tests for GameServer class."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import websockets
from websockets.server import WebSocketServerProtocol

from dicerealms.server.server import GameServer


@pytest.fixture
def server():
    """Create a GameServer instance for testing."""
    return GameServer(host="localhost", port=8765)


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    ws = AsyncMock(spec=WebSocketServerProtocol)
    ws.send = AsyncMock()
    return ws


class TestGameServer:
    """Test suite for GameServer."""

    def test_initialization(self, server):
        """Test GameServer initializes correctly."""
        assert server.host == "localhost"
        assert server.port == 8765
        assert len(server.connected_clients) == 0
        assert len(server.player_names) == 0
        assert server.turn_manager is not None

    @pytest.mark.asyncio
    async def test_handle_client_connection(self, server, mock_websocket):
        """Test handling a new client connection."""
        # Mock the websocket iteration
        async def mock_iter():
            yield json.dumps({"type": "connect", "player_name": "Alice"})
            # Simulate connection close
            raise websockets.exceptions.ConnectionClosed(None, None)
        
        mock_websocket.__aiter__ = lambda self: mock_iter()
        
        # Mock send_to_client to capture messages
        sent_messages = []
        async def capture_send(player_id, message):
            sent_messages.append((player_id, message))
        
        server.send_to_client = capture_send
        
        await server.handle_client(mock_websocket)
        
        # Check welcome message was sent
        assert len(sent_messages) >= 1
        welcome_msg = sent_messages[0][1]
        assert welcome_msg["type"] == "welcome"
        assert "player_id" in welcome_msg

    @pytest.mark.asyncio
    async def test_handle_connect_message(self, server):
        """Test handling connect message."""
        player_id = "player_1"
        server.connected_clients[player_id] = AsyncMock()
        server.connected_clients[player_id].send = AsyncMock()
        server.broadcast = AsyncMock()
        
        message = {"type": "connect", "player_name": "Alice"}
        await server.handle_connect(player_id, message)
        
        assert server.player_names[player_id] == "Alice"
        server.broadcast.assert_called_once()
        server.connected_clients[player_id].send.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_chat_message(self, server):
        """Test handling chat message."""
        player_id = "player_1"
        server.player_names[player_id] = "Alice"
        server.broadcast = AsyncMock()
        
        message = {"type": "chat", "message": "Hello!"}
        await server.handle_chat(player_id, message)
        
        server.broadcast.assert_called_once()
        broadcast_msg = server.broadcast.call_args[0][0]
        assert broadcast_msg["type"] == "chat"
        assert broadcast_msg["player"] == "Alice"
        assert broadcast_msg["message"] == "Hello!"

    @pytest.mark.asyncio
    async def test_handle_action_not_your_turn(self, server):
        """Test handling action when it's not player's turn."""
        player_id = "player_1"
        other_player = "player_2"
        server.player_names[player_id] = "Alice"
        server.connected_clients[player_id] = AsyncMock()
        server.connected_clients[player_id].send = AsyncMock()
        
        # Set other player as current
        server.turn_manager.add_player(other_player)
        server.turn_manager.add_player(player_id)
        
        message = {"type": "action", "action": "roll", "args": ["1d6"]}
        await server.handle_action(player_id, message)
        
        # Should send error message
        server.connected_clients[player_id].send.assert_called_once()
        sent_msg = json.loads(server.connected_clients[player_id].send.call_args[0][0])
        assert sent_msg["type"] == "error"
        assert "not your turn" in sent_msg["message"].lower()

    @pytest.mark.asyncio
    async def test_handle_action_valid_turn(self, server):
        """Test handling action when it's player's turn."""
        player_id = "player_1"
        server.player_names[player_id] = "Alice"
        server.connected_clients[player_id] = AsyncMock()
        server.broadcast = AsyncMock()
        
        # Set player as current
        server.turn_manager.add_player(player_id)
        
        message = {"type": "action", "action": "roll", "args": ["1d6"]}
        await server.handle_action(player_id, message)
        
        # Should broadcast action result
        server.broadcast.assert_called()
        broadcast_msg = server.broadcast.call_args[0][0]
        assert broadcast_msg["type"] == "action_result"
        assert broadcast_msg["player"] == "Alice"
        assert broadcast_msg["action"] == "roll"

    @pytest.mark.asyncio
    async def test_send_to_client(self, server, mock_websocket):
        """Test sending message to specific client."""
        player_id = "player_1"
        server.connected_clients[player_id] = mock_websocket
        
        message = {"type": "test", "data": "test"}
        await server.send_to_client(player_id, message)
        
        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])
        assert sent_data == message

    @pytest.mark.asyncio
    async def test_broadcast(self, server):
        """Test broadcasting message to all clients."""
        # Create multiple mock clients
        client1 = AsyncMock()
        client1.send = AsyncMock()
        client2 = AsyncMock()
        client2.send = AsyncMock()
        
        server.connected_clients = {
            "player_1": client1,
            "player_2": client2
        }
        
        message = {"type": "test", "data": "broadcast"}
        await server.broadcast(message)
        
        # Both clients should receive the message
        assert client1.send.call_count == 1
        assert client2.send.call_count == 1

    @pytest.mark.asyncio
    async def test_handle_message_unknown_type(self, server):
        """Test handling unknown message type."""
        player_id = "player_1"
        server.connected_clients[player_id] = AsyncMock()
        server.connected_clients[player_id].send = AsyncMock()
        
        raw_message = json.dumps({"type": "unknown_type", "data": "test"})
        await server.handle_message(player_id, raw_message)
        
        # Should send error message
        server.connected_clients[player_id].send.assert_called_once()
        sent_msg = json.loads(server.connected_clients[player_id].send.call_args[0][0])
        assert sent_msg["type"] == "error"
        assert "unknown message type" in sent_msg["message"].lower()

    @pytest.mark.asyncio
    async def test_handle_message_invalid_json(self, server):
        """Test handling invalid JSON message."""
        player_id = "player_1"
        server.connected_clients[player_id] = AsyncMock()
        server.connected_clients[player_id].send = AsyncMock()
        
        await server.handle_message(player_id, "invalid json")
        
        # Should send error message
        server.connected_clients[player_id].send.assert_called_once()
        sent_msg = json.loads(server.connected_clients[player_id].send.call_args[0][0])
        assert sent_msg["type"] == "error"
        assert "invalid json" in sent_msg["message"].lower()