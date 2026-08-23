from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True, slots=True)
class WebConsoleSettings:
    repository_root: Path
    python_executable: Path
    artifacts_root: Path
    database_path: Path
    max_concurrent: int = 2

    @classmethod
    def default(cls) -> "WebConsoleSettings":
        root = Path(__file__).resolve().parents[1]
        artifacts = root / "artifacts"
        return cls(root, Path(sys.executable), artifacts, artifacts / "temp" / "web_console" / "web_console.sqlite3")
