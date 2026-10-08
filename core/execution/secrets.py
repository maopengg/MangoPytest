"""运行参数的敏感字段识别与脱敏。

真实凭据禁止入库、禁止回显（见仓库根 ``AGENTS.md``）。运行参数覆盖
（``runtime_overrides``）会随控制台运行记录落库，因此所有对外暴露的路径都必须
先经过本模块脱敏；执行链路内部仍使用未脱敏的原值。

设计约束：**只在"读出/对外"边界脱敏，不在"写入"边界脱敏**。原因是
``web_console/run_service.py`` 在执行时会从数据库读回 ``runtime_overrides``
重新构造子进程环境，写入侧脱敏会让运行拿到一串掩码并静默失效。
"""

from __future__ import annotations

from typing import Any, Mapping

# 命中任一标记即视为敏感字段（大小写不敏感）。
SENSITIVE_KEY_MARKERS = (
    "API_KEY",
    "APIKEY",
    "ACCESS_KEY",
    "SECRET_KEY",
    "PRIVATE_KEY",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "CREDENTIAL",
)

_MASK = "*" * 8


def is_sensitive_key(key: Any) -> bool:
    """判断配置项名是否属于敏感字段。"""

    upper = str(key).upper()
    return any(marker in upper for marker in SENSITIVE_KEY_MARKERS)


def mask_secret(value: Any) -> str:
    """把凭据值替换为不可还原的掩码，保留少量首尾字符便于核对。"""

    if value is None:
        return ""
    text = str(value)
    if not text:
        return ""
    if len(text) <= 8:
        return _MASK
    return f"{text[:4]}{_MASK}{text[-4:]}"


def redact_overrides(values: Mapping[str, Any] | None) -> dict[str, Any]:
    """对外输出的运行参数：敏感字段只保留掩码。"""

    result: dict[str, Any] = {}
    for key, value in (values or {}).items():
        result[key] = mask_secret(value) if is_sensitive_key(key) else value
    return result


def strip_sensitive(values: Mapping[str, Any] | None) -> dict[str, Any]:
    """删除敏感字段，用于清理历史遗留的明文记录。

    这里选择"删除"而不是"打码"：打码后的值一旦被重跑取用，会以一个无意义的
    字符串去访问外部服务，产生难以排查的失败；删除后该次运行会自然回退到
    环境变量或 CI Secret。
    """

    return {
        key: value
        for key, value in (values or {}).items()
        if not is_sensitive_key(key)
    }


__all__ = [
    "SENSITIVE_KEY_MARKERS",
    "is_sensitive_key",
    "mask_secret",
    "redact_overrides",
    "strip_sensitive",
]
