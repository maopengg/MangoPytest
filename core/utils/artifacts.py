"""仓库级运行产物路径。"""

from pathlib import Path


ARTIFACT_ROOT = Path(__file__).resolve().parents[2] / "artifacts"


def artifact_path(*parts: str) -> str:
    """返回 ``artifacts/`` 下的绝对路径，避免受 pytest cwd 影响。"""

    return str(ARTIFACT_ROOT.joinpath(*parts))
