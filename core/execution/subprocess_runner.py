from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import os
import signal

from core.execution.models import RunCommand


async def run_subprocess(command: RunCommand, on_line: Callable[[str], Awaitable[None]],
                         on_started: Callable[[asyncio.subprocess.Process], Awaitable[None]] | None = None) -> int:
    process = await asyncio.create_subprocess_exec(
        *command.argv, cwd=command.cwd, env=command.environment,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        start_new_session=os.name != "nt",
    )
    if on_started:
        await on_started(process)
    assert process.stdout is not None
    while line := await process.stdout.readline():
        await on_line(line.decode("utf-8", errors="replace").rstrip("\n"))
    return await process.wait()


async def terminate_process(process: asyncio.subprocess.Process, timeout: float = 5.0) -> None:
    if process.returncode is not None:
        return
    process.terminate() if os.name == "nt" else os.killpg(process.pid, signal.SIGTERM)
    try:
        await asyncio.wait_for(process.wait(), timeout)
        return
    except TimeoutError:
        pass
    process.kill() if os.name == "nt" else os.killpg(process.pid, signal.SIGKILL)
    await process.wait()
