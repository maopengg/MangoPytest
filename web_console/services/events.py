"""执行事件文件的写入与增量读取，不依赖 HTTP 框架。"""

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import datetime, timezone
import json
from pathlib import Path

from core.execution.models import FINAL_STATUSES
from web_console.repositories.runs import RunRepository


class RunEventService:
    def __init__(self, repository: RunRepository):
        self.repository = repository

    def path(self, run_id: str) -> Path:
        record = self.repository.get(run_id)
        if not record:
            raise ValueError("执行记录不存在")
        return Path(record["artifact_dir"]) / "events.ndjson"

    def write(self, record: dict, event_type: str, message: str) -> None:
        directory = Path(record["artifact_dir"])
        directory.mkdir(parents=True, exist_ok=True)
        event = {"time": datetime.now(timezone.utc).isoformat(), "type": event_type, "message": message}
        with (directory / "events.ndjson").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        if event_type == "log":
            with (directory / "stdout.log").open("a", encoding="utf-8") as stream:
                stream.write(message + "\n")

    async def stream(
        self, run_id: str, event_path: Path,
        disconnected: Callable[[], Awaitable[bool]],
    ) -> AsyncIterator[str]:
        position = 0
        while True:
            if event_path.is_file():
                with event_path.open(encoding="utf-8") as source:
                    source.seek(position)
                    for line in source:
                        payload = line.rstrip("\n")
                        yield f"data: {payload}\n\n"
                    position = source.tell()
            current = self.repository.get(run_id)
            if current and current["status"] in {status.value for status in FINAL_STATUSES}:
                yield f"event: end\ndata: {json.dumps({'status': current['status']})}\n\n"
                return
            if await disconnected():
                return
            yield ": keepalive\n\n"
            await asyncio.sleep(0.5)
