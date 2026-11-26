from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

from core.runtime import runtime_root


@dataclass(frozen=True, slots=True)
class WebConsoleSettings:
    repository_root: Path
    python_executable: Path
    runtime_root: Path
    database_path: Path
    max_concurrent: int = 2

    @classmethod
    def default(cls) -> "WebConsoleSettings":
        root = Path(__file__).resolve().parents[1]
        runtime = runtime_root(root)
        return cls(root, Path(sys.executable), runtime, runtime / "cache" / "web_console" / "web_console.sqlite3")
