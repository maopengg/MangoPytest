from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from core.execution import CommandBuilder, ProjectCatalog, RunOptions, RunStatus, TargetKind
from core.execution.models import FINAL_STATUSES
from core.execution.result_parser import parse_junit, status_from_exit_code
from core.execution.subprocess_runner import run_subprocess, terminate_process
from web_console.config import WebConsoleSettings
from web_console.collection_service import CollectionService
from web_console.repository import RunRepository
from web_console.schemas import CreateRunInput


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunService:
    def __init__(
        self,
        settings: WebConsoleSettings,
        catalog: ProjectCatalog,
        repository: RunRepository,
        collector: CollectionService,
    ) -> None:
        self.settings = settings
        self.catalog = catalog
        self.repository = repository
        self.collector = collector
        self.builder = CommandBuilder(settings.python_executable)
        self.semaphore = asyncio.Semaphore(settings.max_concurrent)
        self.ui_semaphore = asyncio.Semaphore(1)
        self.project_locks: dict[str, asyncio.Lock] = {}
        self.tasks: dict[str, asyncio.Task] = {}
        self.processes: dict[str, asyncio.subprocess.Process] = {}

    def create(self, data: CreateRunInput) -> dict:
        project = self.catalog.get(data.project)
        available_environments = {profile["id"] for profile in self.catalog.environment_profiles(data.project)}
        if data.environment not in available_environments:
            raise ValueError(f"项目 {data.project} 不存在环境配置: {data.environment}")
        if data.environment == "prod" and data.production_confirmation != data.project:
            raise ValueError("生产环境执行必须输入项目 ID 进行确认")
        target_kind = TargetKind(data.target.type)
        feature_nodes = self._feature_nodes(data.project, target_kind, data.target.id)
        options = RunOptions(
            markers=tuple(data.options.markers), keyword=data.options.keyword,
            workers=data.options.workers, reruns=data.options.reruns,
            max_failures=data.options.max_failures,
        )
        runtime_overrides = self.catalog.validate_runtime_overrides(
            data.project, data.runtime_overrides
        )
        # 创建记录前先完整验证路径与参数。
        self.builder.build(
            project, data.environment, target_kind, data.target.id, options,
            runtime_overrides=runtime_overrides,
            feature_nodes=feature_nodes,
        )
        run_id = uuid.uuid4().hex
        artifact_dir = (self.settings.artifacts_root / "reports" / "runs" / run_id).resolve()
        record = {
            "id": run_id, "project": project.id, "project_kind": project.kind,
            "environment": data.environment, "target_kind": target_kind.value, "target": data.target.id,
            "options_json": json.dumps(data.options.model_dump(), ensure_ascii=False),
            "runtime_overrides_json": json.dumps(runtime_overrides, ensure_ascii=False),
            "status": RunStatus.QUEUED.value, "created_at": now(), "artifact_dir": str(artifact_dir),
        }
        self.repository.create(record)
        self.tasks[run_id] = asyncio.create_task(self._execute(run_id), name=f"pytest-run-{run_id}")
        return self.repository.get(run_id)

    async def _execute(self, run_id: str) -> None:
        record = self.repository.get(run_id)
        if not record:
            return
        project_lock = self.project_locks.setdefault(record["project"], asyncio.Lock())
        try:
            async with self.semaphore, project_lock:
                if self.repository.get(run_id)["status"] == RunStatus.CANCELLED.value:
                    return
                if record["project_kind"] == "ui":
                    async with self.ui_semaphore:
                        await self._run_process(record)
                else:
                    await self._run_process(record)
        except asyncio.CancelledError:
            if current := self.repository.get(run_id):
                if current["status"] not in {item.value for item in FINAL_STATUSES}:
                    self.repository.update(run_id, status=RunStatus.CANCELLED.value, finished_at=now(), message="任务已取消")
            raise
        except Exception as exc:
            await self._event(record, "error", str(exc))
            self.repository.update(run_id, status=RunStatus.ERROR.value, finished_at=now(), message=str(exc))
        finally:
            self.processes.pop(run_id, None)
            self.tasks.pop(run_id, None)

    async def _run_process(self, record: dict) -> None:
        run_id = record["id"]
        artifact_dir = Path(record["artifact_dir"])
        allure_dir = artifact_dir / "allure-results"
        junit_path = artifact_dir / "junit.xml"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        options = RunOptions(**{**record["options"], "markers": tuple(record["options"]["markers"])})
        command = self.builder.build(
            self.catalog.get(record["project"]), record["environment"], TargetKind(record["target_kind"]),
            record["target"], options, junit_path=junit_path, allure_dir=allure_dir,
            runtime_overrides=record["runtime_overrides"],
            feature_nodes=self._feature_nodes(
                record["project"], TargetKind(record["target_kind"]), record["target"]
            ),
        )
        self.repository.update(run_id, status=RunStatus.RUNNING.value, started_at=now(), command=command.display)
        await self._event(record, "status", "running")

        async def started(process: asyncio.subprocess.Process) -> None:
            self.processes[run_id] = process
            self.repository.update(run_id, pid=process.pid)

        async def line_received(line: str) -> None:
            await self._event(record, "log", line)

        exit_code = await run_subprocess(command, line_received, started)
        current = self.repository.get(run_id)
        if current and current["status"] == RunStatus.CANCELLED.value:
            return
        summary = parse_junit(junit_path)
        status = status_from_exit_code(exit_code)
        (artifact_dir / "summary.json").write_text(
            json.dumps({**summary, "status": status.value, "exit_code": exit_code}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.repository.update(
            run_id, status=status.value, exit_code=exit_code, finished_at=now(), pid=None, **summary,
        )
        await self._event(record, "status", status.value)

    def _feature_nodes(self, project_id: str, kind: TargetKind, target: str) -> tuple[str, ...]:
        if kind is not TargetKind.FEATURE:
            return ()
        return self.collector.feature_nodes(project_id, target)

    async def _event(self, record: dict, event_type: str, message: str) -> None:
        artifact_dir = Path(record["artifact_dir"])
        artifact_dir.mkdir(parents=True, exist_ok=True)
        event = {"time": now(), "type": event_type, "message": message}
        with (artifact_dir / "events.ndjson").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        if event_type == "log":
            with (artifact_dir / "stdout.log").open("a", encoding="utf-8") as stream:
                stream.write(message + "\n")

    async def cancel(self, run_id: str) -> dict:
        record = self.repository.get(run_id)
        if not record:
            raise ValueError("执行记录不存在")
        if record["status"] in {item.value for item in FINAL_STATUSES}:
            return record
        self.repository.update(run_id, status=RunStatus.CANCELLED.value, finished_at=now(), message="用户取消")
        if process := self.processes.get(run_id):
            await terminate_process(process)
        elif task := self.tasks.get(run_id):
            task.cancel()
        await self._event(record, "status", "cancelled")
        return self.repository.get(run_id)

    async def shutdown(self) -> None:
        for run_id in tuple(self.processes):
            await self.cancel(run_id)
        pending = tuple(self.tasks.values())
        for task in pending:
            if not task.done():
                task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
