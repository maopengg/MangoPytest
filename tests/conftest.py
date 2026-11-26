"""公共框架测试只装配临时样例项目，不读取业务项目配置。"""

from pathlib import Path
import sys

import pytest


@pytest.fixture
def repository_root():
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_project_root(tmp_path, monkeypatch):
    from core.enums.tools_enum import AutoTestTypeEnum
    import core.execution.catalog as catalog_module

    root = tmp_path / "sample-repository"
    registry = {}
    for name, kind in (
        ("sample_api", AutoTestTypeEnum.API),
        ("sample_bdd", AutoTestTypeEnum.API),
        ("sample_secondary_api", AutoTestTypeEnum.API),
        ("sample_ui", AutoTestTypeEnum.UI),
    ):
        project = root / "auto_tests" / name
        (project / "config").mkdir(parents=True)
        (project / "config/.env.test").write_text(
            "BASE_URL=https://api.example.test\nMOCK_TIMEOUT=30\n", encoding="utf-8"
        )
        (project / "test_sample.py").write_text("def test_ok():\n    assert True\n")
        registry[name] = {
            "type": kind, "project_name": name, "path": name, "enabled": True,
            "environments": {"test": {"label": "测试", "config_file": "config/.env.test"}},
            "runtime_options": (
                {"key": "BASE_URL", "label": "服务地址", "type": "url"},
                {"key": "MOCK_TIMEOUT", "label": "超时", "type": "integer",
                 "default": "30", "min": 1, "max": 300},
            ),
        }
    monkeypatch.setattr(catalog_module, "PROJECT_REGISTRY", registry)
    return root


@pytest.fixture
def console_settings(tmp_path, sample_project_root):
    from web_console.config import WebConsoleSettings

    return WebConsoleSettings(
        repository_root=sample_project_root,
        python_executable=Path(sys.executable),
        runtime_root=tmp_path / "runtime",
        database_path=tmp_path / "web.sqlite3",
    )
