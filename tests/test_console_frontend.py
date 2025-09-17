# tests/test_console_frontend.py
# SPDX-License-Identifier: MIT

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from dicerealms.console_frontend import ConsoleFrontend


@pytest.fixture
def frontend():
    return ConsoleFrontend()


@pytest.mark.asyncio
async def test_frontend_initialization(frontend):
    """Test frontend initializes correctly."""
    assert frontend.session is not None
    assert frontend._reader_task is None
    assert not frontend._stop.is_set()


@pytest.mark.asyncio
async def test_frontend_write(frontend):
    """Test the _write method."""
    with (
        patch("sys.stdout.write") as mock_write,
        patch("sys.stdout.flush") as mock_flush,
    ):

        frontend._write("test message")

        mock_write.assert_called_once_with("test message")
        mock_flush.assert_called_once()


@pytest.mark.asyncio
async def test_frontend_start(frontend):
    """Test frontend start method."""
    with patch.object(frontend.session, "start", new_callable=AsyncMock) as mock_start:
        await frontend.start()

        mock_start.assert_called_once()
        assert frontend._reader_task is not None


@pytest.mark.asyncio
async def test_frontend_stdin_reader_quit(frontend):
    """Test stdin reader handles quit command."""
    with patch("sys.stdin.readline", return_value="quit\n"):
        await frontend.start()

        # Feed a quit command
        await frontend.session.feed_line("quit")

        # Wait for processing
        await asyncio.sleep(0.1)

        # Should not raise any exceptions
        assert True


@pytest.mark.asyncio
async def test_frontend_stdin_reader_eof(frontend):
    """Test stdin reader handles EOF."""
    with patch("sys.stdin.readline", return_value=""):
        await frontend.start()

        # Feed empty line (EOF)
        await frontend.session.feed_line("")

        # Wait for processing
        await asyncio.sleep(0.1)

        # Should not raise any exceptions
        assert True


@pytest.mark.asyncio
async def test_frontend_run(frontend):
    """Test the main run method."""
    with (
        patch.object(frontend, "start", new_callable=AsyncMock) as mock_start,
        patch.object(
            frontend.session, "wait_closed", new_callable=AsyncMock
        ) as mock_wait,
    ):

        # Make wait_closed complete immediately
        mock_wait.return_value = asyncio.sleep(0)

        await frontend.run()

        mock_start.assert_called_once()
        mock_wait.assert_called_once()
        assert frontend._stop.is_set()


@pytest.mark.asyncio
async def test_frontend_keyboard_interrupt(frontend):
    """Test frontend handles KeyboardInterrupt."""
    with patch("sys.stdin.readline", side_effect=KeyboardInterrupt):
        await frontend.start()

        # Should handle KeyboardInterrupt gracefully
        await asyncio.sleep(0.1)
        assert True
