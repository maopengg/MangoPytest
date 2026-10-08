from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Any

from core.execution.secrets import strip_sensitive


class RunRepository:
    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = RLock()
        with self.connection:
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, project TEXT NOT NULL, project_kind TEXT NOT NULL,
                    environment TEXT NOT NULL, target_kind TEXT NOT NULL, target TEXT NOT NULL,
                    options_json TEXT NOT NULL, status TEXT NOT NULL, pid INTEGER,
                    command TEXT NOT NULL DEFAULT '', exit_code INTEGER,
                    total INTEGER NOT NULL DEFAULT 0, passed INTEGER NOT NULL DEFAULT 0,
                    failed INTEGER NOT NULL DEFAULT 0, errors INTEGER NOT NULL DEFAULT 0,
                    skipped INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL,
                    started_at TEXT, finished_at TEXT, artifact_dir TEXT NOT NULL,
                    message TEXT NOT NULL DEFAULT ''
                )
            """)
            columns = {row[1] for row in self.connection.execute("PRAGMA table_info(runs)")}
            if "runtime_overrides_json" not in columns:
                self.connection.execute(
                    "ALTER TABLE runs ADD COLUMN runtime_overrides_json TEXT NOT NULL DEFAULT '{}'"
                )
        self._scrub_legacy_secrets()

    def _scrub_legacy_secrets(self) -> None:
        """清理历史运行记录中遗留的明文凭据。

        早期控制台允许填写 AI API Key 并原文落库（违反 ``AGENTS.md``）。这里在启动时
        一次性删除这些字段：打码不可取，因为重跑会拿掩码去访问外部服务而产生难以排查
        的失败；删除后该次运行会自然回退到环境变量 / CI Secret。
        """

        with self.lock, self.connection:
            rows = self.connection.execute(
                "SELECT id, runtime_overrides_json FROM runs "
                "WHERE runtime_overrides_json NOT IN ('', '{}')"
            ).fetchall()
            for row in rows:
                try:
                    values = json.loads(row["runtime_overrides_json"] or "{}")
                except json.JSONDecodeError:
                    values = None
                if not isinstance(values, dict):
                    # 无法解析的历史载荷统一归零，避免读取路径 json.loads 抛异常。
                    self.connection.execute(
                        "UPDATE runs SET runtime_overrides_json='{}' WHERE id=?", (row["id"],)
                    )
                    continue
                scrubbed = strip_sensitive(values)
                if scrubbed != values:
                    self.connection.execute(
                        "UPDATE runs SET runtime_overrides_json=? WHERE id=?",
                        (json.dumps(scrubbed, ensure_ascii=False), row["id"]),
                    )

    def create(self, record: dict[str, Any]) -> None:
        columns = ",".join(record)
        placeholders = ",".join("?" for _ in record)
        with self.lock, self.connection:
            self.connection.execute(f"INSERT INTO runs ({columns}) VALUES ({placeholders})", tuple(record.values()))

    def update(self, run_id: str, **values: Any) -> None:
        if not values:
            return
        assignment = ",".join(f"{column}=?" for column in values)
        with self.lock, self.connection:
            self.connection.execute(f"UPDATE runs SET {assignment} WHERE id=?", (*values.values(), run_id))

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self.lock:
            row = self.connection.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        return self._convert(row) if row else None

    def list(
        self, limit: int = 100, project: str = "", status: str = "", offset: int = 0
    ) -> list[dict[str, Any]]:
        where, params = [], []
        if project:
            where.append("project=?")
            params.append(project)
        if status:
            where.append("status=?")
            params.append(status)
        clause = " WHERE " + " AND ".join(where) if where else ""
        page_limit = max(1, min(limit, 500))
        page_offset = max(0, offset)
        with self.lock:
            rows = self.connection.execute(
                f"SELECT * FROM runs{clause} ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                (*params, page_limit, page_offset),
            ).fetchall()
        return [self._convert(row) for row in rows]

    def interrupt_stale(self) -> None:
        with self.lock, self.connection:
            self.connection.execute(
                "UPDATE runs SET status='interrupted', finished_at=datetime('now'), message='控制台重启，任务状态已恢复' "
                "WHERE status IN ('queued','running')"
            )

    @staticmethod
    def _convert(row: sqlite3.Row) -> dict[str, Any]:
        value = dict(row)
        value["options"] = json.loads(value.pop("options_json"))
        value["runtime_overrides"] = json.loads(value.pop("runtime_overrides_json", "{}"))
        return value
