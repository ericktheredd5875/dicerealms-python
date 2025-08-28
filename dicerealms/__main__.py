# SPDX-License-Identifier: MIT
import asyncio

from dicerealms.console_frontend import ConsoleFrontend


async def main():
    frontend = ConsoleFrontend()
    await frontend.run()


if __name__ == "__main__":
    asyncio.run(main())
