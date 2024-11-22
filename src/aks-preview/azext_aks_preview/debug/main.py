import asyncio

from .controller.rule_orchestrator import Orchestrator
from collections import namedtuple


async def main():
    orchestrator = Orchestrator()
    await orchestrator.run("dns")
    return

if __name__ == "__main__":
    asyncio.run(main())
