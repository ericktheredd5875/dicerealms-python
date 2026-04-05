# SPDX-License-Identifier: MIT
import asyncio

from dicerealms.engine import GameEngine
from dicerealms.world import load_default_world
from dicerealms.player import Player

class GameSession:
    """
    A single player's session: reads commands from an input queue, passess them
    to the Engine, and writes responses via a callback.
    """

    def __init__(self, write_callback):
        self.player = Player()
        self.world = load_default_world()

        self.engine = GameEngine(world=self.world, player=self.player)
        self.incoming: asyncio.Queue[str] = asyncio.Queue()
        self.write = write_callback
        self._task: asyncio.Task | None = None
        self._closed = asyncio.Event()

    async def start(self):
        self.write("Welcome to DiceRealms (alpha). Type 'help' to begin.\n")
        self.write("You are in " + self.world.look(self.player.room) + "\n\n")
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
