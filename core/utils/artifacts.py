"""测试产物统一存放在运行目录，保留业务侧的产物路径入口。"""

from core.runtime import runtime_path


def artifact_path(*parts: str) -> str:
    """返回 ``runtime/`` 下的绝对路径，避免受 pytest cwd 影响。"""

    return runtime_path(*parts)
