from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Any


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

    def list(self, limit: int = 100, project: str = "", status: str = "") -> list[dict[str, Any]]:
        where, params = [], []
        if project:
            where.append("project=?")
            params.append(project)
        if status:
            where.append("status=?")
            params.append(status)
        clause = " WHERE " + " AND ".join(where) if where else ""
        with self.lock:
            rows = self.connection.execute(
                f"SELECT * FROM runs{clause} ORDER BY created_at DESC LIMIT ?", (*params, min(limit, 500))
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
        return value
