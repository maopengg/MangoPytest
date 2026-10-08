"""运行参数敏感字段的识别、脱敏与合规约束。

真实凭据禁止入库、禁止回显（``AGENTS.md``）。这里锁定三条不变量：

1. 控制台不再提供 ``AI_API_KEY`` 输入，凭据只允许由环境变量 / CI Secret 注入；
2. 数据库保留原值（执行链路要从库里读回 overrides 重建子进程环境），
   对外 API 只回掩码；
3. 历史遗留的明文凭据在仓库初始化时被清除。
"""

import json
from pathlib import Path

from core.execution.catalog import ProjectCatalog
from core.execution.secrets import (
    is_sensitive_key,
    mask_secret,
    redact_overrides,
    strip_sensitive,
)
from web_console.app import public_run
from web_console.repository import RunRepository


def test_sensitive_key_detection_covers_common_credential_names() -> None:
    for key in (
        "AI_API_KEY",
        "MANGO_MOCK_ADMIN_TOKEN",
        "DB_PASSWORD",
        "AWS_SECRET_KEY",
        "GITHUB_ACCESS_KEY",
        "SERVICE_CREDENTIAL",
    ):
        assert is_sensitive_key(key), key
    for key in ("AI_MODEL", "BASE_URL", "MOCK_TIMEOUT", "HEADLESS", "TRACE_ENABLED"):
        assert not is_sensitive_key(key), key


def test_mask_secret_never_reveals_middle_of_value() -> None:
    masked = mask_secret("sk-1234567890abcdef")
    assert masked == "sk-1********cdef"
    assert "234567890abc" not in masked
    # 短值整体掩码，避免"保留首尾"反而泄露大部分内容。
    assert mask_secret("short") == "********"
    assert mask_secret("") == ""
    assert mask_secret(None) == ""


def test_redact_and_strip_only_touch_sensitive_keys() -> None:
    values = {
        "AI_API_KEY": "sk-1234567890abcdef",
        "MANGO_MOCK_ADMIN_TOKEN": "token-value",
        "AI_MODEL": "glm-4",
        "BASE_URL": "http://43.142.161.61:8003",
    }
    assert redact_overrides(values) == {
        "AI_API_KEY": "sk-1********cdef",
        "MANGO_MOCK_ADMIN_TOKEN": "toke********alue",
        "AI_MODEL": "glm-4",
        "BASE_URL": "http://43.142.161.61:8003",
    }
    assert strip_sensitive(values) == {
        "AI_MODEL": "glm-4",
        "BASE_URL": "http://43.142.161.61:8003",
    }


def test_console_no_longer_declares_credential_or_dead_healing_mode_option() -> None:
    """控制台不得再暴露凭据输入，也不得暴露在 2.1.0 下无效的自愈模式。"""

    from auto_tests.project_registry import UI_RUNTIME_OPTIONS

    keys = {option["key"] for option in UI_RUNTIME_OPTIONS}
    assert "AI_API_KEY" not in keys
    assert "ELEMENT_HEALING_MODE" not in keys
    assert {"AI_ELEMENT_HEALING_ENABLED", "AI_BASE_URL", "AI_MODEL"} <= keys


def test_catalog_preview_allows_ai_settings_but_masks_credentials(tmp_path: Path) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(
        "BASE_URL=http://43.142.161.61:8003\n"
        "AI_MODEL=glm-4\n"
        "AI_ELEMENT_HEALING_ENABLED=true\n"
        "AI_API_KEY=sk-1234567890abcdef\n"
        "UNRELATED=ignored\n",
        encoding="utf-8",
    )

    values = ProjectCatalog._safe_env_values(env_file)

    assert values["AI_MODEL"] == "glm-4"
    assert values["AI_ELEMENT_HEALING_ENABLED"] == "true"
    assert values["AI_API_KEY"] == "sk-1********cdef"
    assert "UNRELATED" not in values


def test_public_run_masks_credential_but_keeps_other_overrides() -> None:
    record = {
        "id": "run-1",
        "runtime_overrides": {
            "AI_API_KEY": "sk-1234567890abcdef",
            "AI_MODEL": "glm-4",
        },
    }

    masked = public_run(record)

    assert masked["runtime_overrides"]["AI_API_KEY"] == "sk-1********cdef"
    assert masked["runtime_overrides"]["AI_MODEL"] == "glm-4"
    # 不得就地修改传入记录，执行链路仍可能持有同一对象。
    assert record["runtime_overrides"]["AI_API_KEY"] == "sk-1234567890abcdef"
    assert public_run(None) is None
    assert public_run({"id": "run-2"}) == {"id": "run-2"}


def test_repository_keeps_real_value_but_scrubs_legacy_plaintext_credentials(
    tmp_path: Path,
) -> None:
    """写入侧保留原值（执行要用），启动时清理历史明文。"""

    database = tmp_path / "runs.sqlite3"
    repository = RunRepository(database)
    overrides = {"AI_API_KEY": "sk-1234567890abcdef", "AI_MODEL": "glm-4"}
    repository.create({
        "id": "run-1", "project": "pytest_api", "project_kind": "api", "environment": "test",
        "target_kind": "project", "target": "", "options_json": "{}",
        "runtime_overrides_json": json.dumps(overrides),
        "status": "queued", "created_at": "2026-01-01T00:00:00Z",
        "artifact_dir": str(tmp_path / "run-1"),
    })

    # 同一连接内不触发清理：执行链路必须能读到原值。
    assert repository.get("run-1")["runtime_overrides"] == overrides

    # 重新打开仓库（等价于控制台重启）后，明文凭据被删除，其余配置保留。
    reopened = RunRepository(database)
    assert reopened.get("run-1")["runtime_overrides"] == {"AI_MODEL": "glm-4"}


def test_legacy_scrub_tolerates_broken_payload(tmp_path: Path) -> None:
    database = tmp_path / "runs.sqlite3"
    repository = RunRepository(database)
    repository.create({
        "id": "run-broken", "project": "pytest_api", "project_kind": "api", "environment": "test",
        "target_kind": "project", "target": "", "options_json": "{}",
        "runtime_overrides_json": "not-json",
        "status": "queued", "created_at": "2026-01-01T00:00:00Z",
        "artifact_dir": str(tmp_path / "run-broken"),
    })

    reopened = RunRepository(database)

    assert reopened.get("run-broken")["runtime_overrides"] == {}
