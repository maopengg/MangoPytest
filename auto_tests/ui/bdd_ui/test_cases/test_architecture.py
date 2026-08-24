"""bdd_ui 大型项目架构门禁。"""

from pathlib import Path

import pytest

from auto_tests.ui.bdd_ui.capabilities.cases import (
    ELEMENT_CASES,
    INVENTORY_CASES,
    OPERATION_CASES,
)
from auto_tests.ui.bdd_ui.config import settings
from core.ui import configured_element_repository

elements = configured_element_repository(settings)

pytestmark = pytest.mark.architecture
PROJECT = Path(__file__).resolve().parents[1]


def test_local_excel_registry_covers_capability_inventory():
    excel_keys = {definition.name for definition in elements.all()}
    inventory_keys = {case.element_id for case in INVENTORY_CASES}
    assert len(excel_keys) >= 260
    assert excel_keys == inventory_keys
    assert len(OPERATION_CASES) >= 103
    assert len(ELEMENT_CASES) >= 130


def test_business_layers_do_not_import_another_ui_demo():
    forbidden = ("auto_tests.ui.simple_ui", "auto_tests.ui.pytest_ui")
    for file in PROJECT.rglob("*.py"):
        if file == Path(__file__):
            continue
        content = file.read_text(encoding="utf-8")
        assert not any(value in content for value in forbidden), file


def test_business_features_use_real_domain_steps():
    for file in (PROJECT / "features" / "business").glob("*.feature"):
        content = file.read_text(encoding="utf-8")
        assert "执行 UI-" not in content, file
        assert "操作交互控件用例" not in content, file
        assert "API 查询到的" in content, file
