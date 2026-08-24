"""pytest_ui 大型项目架构门禁。"""

from pathlib import Path

import pytest

from auto_tests.ui.pytest_ui.capabilities.cases import (
    ELEMENT_CASES,
    INVENTORY_CASES,
    OPERATION_CASES,
)
from auto_tests.ui.pytest_ui.config import settings
from core.ui import configured_element_repository

elements = configured_element_repository(settings)

pytestmark = pytest.mark.architecture
PROJECT = Path(__file__).resolve().parents[1]
COMMON_UI_BUSINESS = (
    PROJECT.parents[1] / "common" / "mango_mock" / "ui_business"
)


def test_local_excel_registry_covers_capability_inventory():
    excel_keys = {definition.name for definition in elements.all()}
    inventory_keys = {case.element_id for case in INVENTORY_CASES}
    assert len(excel_keys) >= 260
    assert excel_keys == inventory_keys
    assert len(OPERATION_CASES) >= 103
    assert len(ELEMENT_CASES) >= 130


def test_business_layers_do_not_import_another_ui_demo():
    test_cases = PROJECT / "test_cases"
    assert len(list((test_cases / "capabilities" / "operations").glob("test_*.py"))) == 12
    assert len(list((test_cases / "capabilities" / "interactions").glob("test_*.py"))) == 5
    assert len(list((test_cases / "capabilities" / "inventory").glob("test_*.py"))) == 8
    assert len(list((test_cases / "business").glob("test_*.py"))) == 3
    assert not (test_cases / "test_mango_mock_ui.py").exists()
    assert not (test_cases / "test_business_workflows.py").exists()
    forbidden = ("auto_tests.ui.simple_ui", "auto_tests.ui.bdd_ui")
    for file in PROJECT.rglob("*.py"):
        if file == Path(__file__):
            continue
        content = file.read_text(encoding="utf-8")
        assert not any(value in content for value in forbidden), file


def test_page_objects_do_not_create_test_data():
    for file in COMMON_UI_BUSINESS.rglob("*.py"):
        content = file.read_text(encoding="utf-8")
        assert "data_factory" not in content, file
        assert "HttpProtocolClient" not in content, file
