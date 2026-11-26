"""统一解析 pytest 的本地运行目录，不依赖当前工作目录。"""

import os
from pathlib import Path


def runtime_root(repository_root: Path | None = None) -> Path:
    repository = (repository_root or Path(__file__).resolve().parents[1]).resolve()
    configured = os.environ.get("MANGO_PYTEST_RUNTIME_DIR", "").strip()
    if not configured:
        return repository / "runtime"
    directory = Path(configured).expanduser()
    return (directory if directory.is_absolute() else repository / directory).resolve()


def runtime_path(*parts: str) -> str:
    return str(runtime_root().joinpath(*parts))
