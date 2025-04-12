import asyncio
from typing import Any

from azure.cli.core.commands import progress


async def poll_helper(progress_hook: progress.ProgressHook, coro, hint: str) -> Any:
    t = asyncio.create_task(coro)
    while True:
        if t.done():
            break
        progress_hook.add(message=hint)
        await asyncio.sleep(2)
    progress_hook.end()
    return t.result()
