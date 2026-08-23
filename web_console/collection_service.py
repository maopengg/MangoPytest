from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from core.execution.catalog import ProjectCatalog
from web_console.config import WebConsoleSettings


class CollectionService:
    def __init__(self, settings: WebConsoleSettings, catalog: ProjectCatalog) -> None:
        self.settings = settings
        self.catalog = catalog
        self.cache_root = settings.artifacts_root / "temp" / "web_console" / "collections"

    def cache_path(self, project_id: str) -> Path:
        return self.cache_root / f"{project_id}.json"

    def read(self, project_id: str) -> dict:
        path = self.cache_path(project_id)
        if not path.is_file():
            return {"count": 0, "cases": [], "collected": False}
        result = json.loads(path.read_text(encoding="utf-8"))
        result["collected"] = True
        return result

    async def collect(self, project_id: str) -> dict:
        project = self.catalog.get(project_id)
        destination = self.cache_path(project_id).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["ENV"] = "test"
        env["PYTHONPATH"] = os.pathsep.join(filter(None, (str(self.settings.repository_root), env.get("PYTHONPATH", ""))))
        process = await asyncio.create_subprocess_exec(
            str(self.settings.python_executable), "-m", "pytest", "--collect-only", "-q",
            "-p", "web_console.pytest_plugin", f"--mango-collect-manifest={destination}",
            cwd=project.root, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        output = (await process.communicate())[0].decode("utf-8", errors="replace")
        if process.returncode != 0 or not destination.is_file():
            raise RuntimeError(f"用例收集失败（exit={process.returncode}）\n{output[-4000:]}")
        return self.read(project_id)

    def tree(self, project_id: str) -> list[dict]:
        project = self.catalog.get(project_id, require_enabled=False)
        cases = self.read(project_id)["cases"]
        files: dict[str, int] = {}
        for case in cases:
            files[case["file"]] = files.get(case["file"], 0) + 1
        visible_files = []
        for path in project.root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".feature"}:
                continue
            relative = path.relative_to(project.root)
            if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
                continue
            value = relative.as_posix()
            visible_files.append({
                "path": value,
                "count": files.get(value, 0),
                "executable": bool(files.get(value, 0)) and path.name.startswith("test_"),
                "type": "feature" if path.suffix == ".feature" else "python",
            })
        return sorted(visible_files, key=lambda item: item["path"])

    def source(self, project_id: str, relative_path: str) -> str:
        project = self.catalog.get(project_id)
        candidate = (project.root / relative_path).resolve()
        if not candidate.is_relative_to(project.root) or not candidate.is_file():
            raise ValueError("文件不存在或路径越界")
        if candidate.suffix not in {".py", ".feature"} or candidate.name.startswith(".env"):
            raise ValueError("该文件类型不允许查看")
        if candidate.stat().st_size > 512_000:
            raise ValueError("文件过大")
        return candidate.read_text(encoding="utf-8", errors="replace")
