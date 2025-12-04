# SPDX-License-Identifier: MIT
import asyncio

# from dicerealms.cli import app
from dicerealms.console_frontend import ConsoleFrontend


async def main():
    frontend = ConsoleFrontend()
    await frontend.run()


def app():  # noqa: F811
    """Entry point for the CLI application."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
