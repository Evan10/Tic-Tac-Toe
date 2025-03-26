
import asyncio
import server.server_main as s
import sys


async def main():
    await s.main()

asyncio.run(main())