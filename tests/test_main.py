# tests/test_main.py
# SPDX-License-Identifier: MIT

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from dicerealms.__main__ import app, main


@pytest.mark.asyncio
async def test_main_function():
    """Test the main async function."""
    with patch("dicerealms.__main__.ConsoleFrontend") as mock_frontend_class:
        mock_frontend = Mock()
        mock_frontend.run = AsyncMock()
        mock_frontend_class.return_value = mock_frontend

        await main()

        mock_frontend_class.assert_called_once()
        mock_frontend.run.assert_called_once()


def test_app_function():
    """Test the app function (entry point)."""
    with patch("asyncio.run") as mock_run:
        app()
        mock_run.assert_called_once()


def test_app_function_with_asyncio_run():
    """Test app function actually calls asyncio.run with main."""
    with patch("asyncio.run") as mock_run:
        app()

        # Check that asyncio.run was called
        mock_run.assert_called_once()

        # Get the coroutine that was passed to asyncio.run
        call_args = mock_run.call_args[0]
        coro = call_args[0]

        # Check that it's a coroutine (not the function itself)
        assert asyncio.iscoroutine(coro)


@pytest.mark.asyncio
async def test_main_creates_console_frontend():
    """Test that main creates a ConsoleFrontend instance."""
    with patch("dicerealms.__main__.ConsoleFrontend") as mock_frontend_class:
        mock_frontend = Mock()
        mock_frontend.run = AsyncMock()
        mock_frontend_class.return_value = mock_frontend

        await main()

        # Verify ConsoleFrontend was instantiated
        mock_frontend_class.assert_called_once_with()


@pytest.mark.asyncio
async def test_main_calls_frontend_run():
    """Test that main calls the frontend's run method."""
    with patch("dicerealms.__main__.ConsoleFrontend") as mock_frontend_class:
        mock_frontend = Mock()
        mock_frontend.run = AsyncMock()
        mock_frontend_class.return_value = mock_frontend

        await main()

        # Verify run method was called
        mock_frontend.run.assert_called_once()


def test_module_execution():
    """Test that the module can be executed directly."""
    with patch("asyncio.run") as mock_run:
        # Simulate running the module directly
        import dicerealms.__main__

        # The module should have set up the if __name__ == "__main__" block
        # but we can't easily test that without actually executing it
        # So we'll just verify the functions exist and are callable
        assert callable(dicerealms.__main__.main)
        assert callable(dicerealms.__main__.app)
