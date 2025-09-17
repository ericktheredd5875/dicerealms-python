# tests/test_session.py
# SPDX-License-Identifier: MIT

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from dicerealms.session import GameSession


@pytest.fixture
def mock_write_callback():
    return Mock()


@pytest.fixture
def session(mock_write_callback):
    return GameSession(mock_write_callback)


@pytest.mark.asyncio
async def test_session_initialization(session, mock_write_callback):
    """Test session initializes correctly."""
    assert session.write == mock_write_callback
    assert session.engine is not None
    assert session.incoming is not None
    assert session._task is None
    assert not session._closed.is_set()


@pytest.mark.asyncio
async def test_session_start(session, mock_write_callback):
    """Test session start method."""
    await session.start()

    # Check that welcome message was written
    mock_write_callback.assert_called_with(
        "Welcome to DiceRealms (alpha). Type 'help' to begin.\n"
    )

    # Check that task was created
    assert session._task is not None
    assert not session._task.done()


@pytest.mark.asyncio
async def test_session_feed_line(session):
    """Test feeding lines to session."""
    await session.feed_line("help")
    await session.feed_line("quit")

    # Check that lines were queued
    assert session.incoming.qsize() == 2


@pytest.mark.asyncio
async def test_session_quit_command(session, mock_write_callback):
    """Test that quit command properly closes session."""
    await session.start()
    await session.feed_line("quit")

    # Wait for session to process and close
    await session.wait_closed()

    # Check that goodbye message was written
    mock_write_callback.assert_called_with("Goodbye!\n")
    assert session._closed.is_set()


@pytest.mark.asyncio
async def test_session_help_command(session, mock_write_callback):
    """Test that help command works through session."""
    await session.start()
    await session.feed_line("help")

    # Give it a moment to process
    await asyncio.sleep(0.1)

    # Check that help response was written
    calls = mock_write_callback.call_args_list
    help_calls = [call for call in calls if "Commands:" in str(call)]
    assert len(help_calls) > 0


@pytest.mark.asyncio
async def test_session_error_handling(session, mock_write_callback):
    """Test that session handles errors gracefully."""
    await session.start()
    await session.feed_line("invalid_command")

    # Give it a moment to process
    await asyncio.sleep(0.1)

    # Check that error message was written
    calls = mock_write_callback.call_args_list
    error_calls = [call for call in calls if "Unknown command" in str(call)]
    assert len(error_calls) > 0


@pytest.mark.asyncio
async def test_session_wait_closed(session):
    """Test wait_closed method."""
    # Initially not closed
    assert not session._closed.is_set()

    # Start session and quit
    await session.start()
    await session.feed_line("quit")

    # Wait for it to close
    await session.wait_closed()
    assert session._closed.is_set()
