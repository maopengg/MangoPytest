"""运行目录、日志落盘和历史迁移的回归验证。"""

import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from core.runtime import runtime_root, runtime_path
from core.base import BaseConfig
from core.utils.project_dir import ProjectDir
from scripts.migrate_runtime import migrate, move_tree
from web_console.config import WebConsoleSettings


def test_runtime_directory_defaults_and_relative_override(tmp_path, monkeypatch):
    monkeypatch.delenv("MANGO_PYTEST_RUNTIME_DIR", raising=False)
    assert runtime_root(tmp_path) == tmp_path / "runtime"
    monkeypatch.setenv("MANGO_PYTEST_RUNTIME_DIR", "local-runtime")
    assert runtime_root(tmp_path) == tmp_path / "local-runtime"


def test_paths_and_console_use_the_same_runtime_root(tmp_path, monkeypatch):
    monkeypatch.setenv("MANGO_PYTEST_RUNTIME_DIR", str(tmp_path))
    directories = ProjectDir()
    assert Path(directories.logs()) == tmp_path / "logs"
    assert Path(directories.cache()) == tmp_path / "cache"
    assert runtime_path("reports", "run-1") == str(tmp_path / "reports/run-1")
    console = WebConsoleSettings.default()
    assert console.runtime_root == tmp_path
    assert console.database_path == tmp_path / "cache/web_console/web_console.sqlite3"

    class ExampleConfig(BaseConfig):
        LOG_DIR: str = "logs/example"
        ALLURE_REPORT_DIR: str = "reports/example/allure"

    config = ExampleConfig(SCREENSHOT_DIR="screenshots/example")
    assert config.LOG_DIR == str(tmp_path / "logs/example")
    assert config.ALLURE_REPORT_DIR == str(tmp_path / "reports/example/allure")
    assert config.SCREENSHOT_DIR == str(tmp_path / "screenshots/example")


def test_log_files_use_executor_level_names(tmp_path):
    environment = {**os.environ, "MANGO_PYTEST_RUNTIME_DIR": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, "-c", "from core.utils import log; "
         "log.debug('runtime-log-probe'); log.info('runtime-log-probe'); "
         "log.warning('runtime-log-probe'); log.error('runtime-log-probe'); "
         "log.critical('runtime-log-probe')"],
        cwd=Path(__file__).resolve().parents[1], env=environment,
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert {p.name for p in (tmp_path / "logs").glob("*.log")} == {
        "debug-log.log", "info-log.log", "warning-log.log", "error-log.log", "critical-log.log",
    }
    assert "runtime-log-probe" in (tmp_path / "logs/info-log.log").read_text()
    assert not (tmp_path / "temp/logs").exists()


def test_direct_pytest_collection_honors_runtime_override(tmp_path):
    repository = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_runtime_paths.py", "--collect-only", "-q"],
        cwd=repository, env={**os.environ, "MANGO_PYTEST_RUNTIME_DIR": str(tmp_path)},
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "cache/pytest/root").is_dir()


def test_migration_preserves_reports_cache_credentials_and_history(tmp_path):
    old = tmp_path / "artifacts"
    run = old / "reports/runs/run-1"
    run.mkdir(parents=True)
    (run / "stdout.log").write_text("original output")
    (old / "temp/logs").mkdir(parents=True)
    (old / "temp/logs/info-log.log").write_text("old log")
    database = old / "temp/web_console/web_console.sqlite3"
    database.parent.mkdir(parents=True)
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE runs (id TEXT, artifact_dir TEXT)")
        connection.execute("INSERT INTO runs VALUES (?, ?)", ("run-1", str(run)))
    limiter = old / "review-limiter"
    limiter.mkdir()
    (limiter / ".env.test").write_text("EXAMPLE=value")
    result = migrate(tmp_path, tmp_path / "runtime")
    assert result["updated_history_paths"] == 1
    assert not old.exists()
    runtime = tmp_path / "runtime"
    assert (runtime / "reports/runs/run-1/stdout.log").read_text() == "original output"
    assert (runtime / "logs/info-log.log").read_text() == "old log"
    assert (runtime / "config/review-limiter/.env.test").read_text() == "EXAMPLE=value"
    with sqlite3.connect(runtime / "cache/web_console/web_console.sqlite3") as connection:
        assert connection.execute("SELECT artifact_dir FROM runs").fetchone()[0] == str(runtime / "reports/runs/run-1")
    assert migrate(tmp_path, runtime)["updated_history_paths"] == 0


def test_migration_never_overwrites_existing_files(tmp_path):
    old = tmp_path / "old.log"
    new = tmp_path / "new.log"
    old.write_text("old")
    new.write_text("new")
    with pytest.raises(FileExistsError):
        move_tree(old, new)
    assert old.read_text() == "old"
    assert new.read_text() == "new"
