# SPDX-License-Identifier: MIT
import asyncio

from dicerealms.engine import GameEngine


class GameSession:
    """
    A single player's session: reads commands from an input queue, passess them
    to the Engine, and writes responses via a callback.
    """

    def __init__(self, write_callback):
        self.engine = GameEngine()
        self.incoming: asyncio.Queue[str] = asyncio.Queue()
        self.write = write_callback
        self._task: asyncio.Task | None = None
        self._closed = asyncio.Event()

    async def start(self):
        self.write("Welcome to DiceRealms (alpha). Type 'help' to begin.\n")
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        try:
            while True:
                line = await self.incoming.get()
                result = self.engine.handle(line)
                if result == "__QUIT__":
                    self.write("Goodbye!\n")
                    break
                if result:
                    self.write(result + "\n")
        finally:
            self._closed.set()

    async def feed_line(self, line: str):
        await self.incoming.put(line)

    async def wait_closed(self):
        await self._closed.wait()
