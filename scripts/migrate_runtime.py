"""停止测试和控制台后，将旧 artifacts 迁入 runtime，保留历史文件与索引。"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.runtime import runtime_root


def move_tree(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        return
    if source.is_dir() and destination.is_dir():
        for child in source.iterdir():
            move_tree(child, destination / child.name)
        source.rmdir()
        return
    raise FileExistsError(f"目标已存在，停止迁移以避免覆盖：{destination}")


def migrate(repository: Path, destination: Path | None = None) -> dict:
    repository = repository.resolve()
    destination = (destination or runtime_root(repository)).resolve()
    if destination == repository or destination in repository.parents:
        raise ValueError("运行目录不能设为源码根目录或其父目录")
    legacy = repository / "artifacts"
    if destination == legacy or legacy in destination.parents:
        raise ValueError("运行目录不能设为旧 artifacts 目录或其子目录")
    move_tree(legacy, destination)
    for old, new in (("temp/logs", "logs"), ("temp/cache", "cache"),
                     ("temp/web_console", "cache/web_console")):
        move_tree(destination / old, destination / new)

    # 历史顶层文件仅整理位置；不覆盖已存在的同名产物。
    for old, new in (("logs", "logs/legacy-root"), ("download", "downloads"),
                     ("screenshot", "screenshots"), ("report", "reports"), ("reports", "reports")):
        move_tree(repository / old, destination / new)
    for item in repository.iterdir():
        if item.is_file() and (item.name.startswith("logs\\") or item.name.startswith(".__logs\\")):
            move_tree(item, destination / "logs/legacy-root" / item.name.split("\\", 1)[1])

    # 项目内旧 pytest 缓存也归入同一缓存根目录。
    for cache in repository.glob("auto_tests/**/.pytest_cache"):
        move_tree(cache, destination / "cache/pytest" / cache.parent.name)
    move_tree(repository / ".pytest_cache", destination / "cache/pytest/root")
    for nested in repository.glob("auto_tests/**/artifacts"):
        if nested.is_dir():
            project = nested.parent.relative_to(repository / "auto_tests")
            move_tree(nested, destination / "reports/legacy-cwd" / project)

    limiter = destination / "review-limiter"
    if limiter.is_dir():
        for item in limiter.iterdir():
            if item.name.startswith(".env."):
                target = destination / "config/review-limiter" / item.name
            elif item.suffix == ".log":
                target = destination / "logs/review-limiter" / item.name
            else:
                target = destination / "reports/review-limiter" / item.name
            move_tree(item, target)
        limiter.rmdir()

    database = destination / "cache/web_console/web_console.sqlite3"
    updated = 0
    if database.is_file():
        with sqlite3.connect(database) as connection:
            for run_id, stored in connection.execute("SELECT id, artifact_dir FROM runs").fetchall():
                if "/artifacts/" not in stored:
                    continue
                relative = stored.split("/artifacts/", 1)[1]
                path = destination / relative
                if path.resolve().is_relative_to(destination) and path.is_dir():
                    connection.execute("UPDATE runs SET artifact_dir=? WHERE id=?", (str(path), run_id))
                    updated += 1
            connection.commit()
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    return {"runtime_root": str(destination), "updated_history_paths": updated}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    arguments = parser.parse_args()
    print(migrate(arguments.root))


if __name__ == "__main__":
    main()
