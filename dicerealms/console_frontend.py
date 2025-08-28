# SPDX-License-Identifier: MIT
import asyncio
import contextlib
import sys

from dicerealms.session import GameSession


class ConsoleFrontend:
    """
    A simple console frontend that:
    - renders output with a write(str) callback
    - reads input lines in a background task
    - forwards lines to the GameSession
    """

    def __init__(self):
        self.session = GameSession(write_callback=self._write)
        self._reader_task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    def _write(self, text: str):
        # stdout is blocking: keep it simple for now.
        sys.stdout.write(text)
        sys.stdout.flush()

    async def start(self):
        await self.session.start()
        # Start a background reader that doesn't block the event loop
        self._reader_task = asyncio.create_task(self._stdin_reader())

    async def _stdin_reader(self):
        loop = asyncio.get_running_loop()
        self._write("> ")
        while not self._stop.is_set():
            # Run blocking input() off-thread so the loop stays responsive
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
            except (KeyboardInterrupt, EOFError):
                line = "quite\n"

            if not line:  # EOF
                line = "quite\n"

            # Strip trailing newlines but preserve an empty command as "".
            clean = line.strip("\r\n")
            await self.session.feed_line(clean)
            if clean.lower() in {"quit", "exit"}:
                break

            self._write("> (HOWDY)")

    async def run(self):
        await self.start()
        await self.session.wait_closed()
        self._stop.set()
        if self._reader_task:
            self._reader_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader_task
