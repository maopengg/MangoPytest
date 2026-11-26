"""执行产物、失败详情及报告读取，统一约束产物访问范围。"""

from pathlib import Path

from core.execution.result_parser import parse_failures
from core.ui.healing_metrics import merge_summaries
from web_console.repositories.runs import RunRepository
from web_console.services.allure import AllureResultService


class ArtifactService:
    def __init__(self, repository: RunRepository):
        self.repository = repository

    def root(self, run_id: str) -> Path:
        record = self.repository.get(run_id)
        if not record:
            raise ValueError("执行记录不存在")
        return Path(record["artifact_dir"]).resolve()

    def failures(self, run_id: str) -> list[dict]:
        return parse_failures(self.root(run_id) / "junit.xml")

    def allure(self, run_id: str) -> dict:
        return AllureResultService(self.root(run_id)).report()

    def ai_healing(self, run_id: str) -> dict:
        root = self.root(run_id)
        merged = merge_summaries(root) if root.is_dir() else None
        return {"available": True, **merged} if merged else {"available": False}

    def list(self, run_id: str) -> list[dict]:
        root = self.root(run_id)
        if not root.is_dir():
            return []
        return [
            {"path": path.relative_to(root).as_posix(), "size": path.stat().st_size}
            for path in sorted(root.rglob("*")) if path.is_file()
        ][:2000]

    def resolve(self, run_id: str, relative_path: str) -> Path:
        root = self.root(run_id)
        candidate = (root / relative_path).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            raise ValueError("产物不存在")
        return candidate
