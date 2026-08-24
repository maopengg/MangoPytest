"""全局 Case 分类、命名和文件组织规范门禁。"""

from __future__ import annotations

import ast
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.execution.case_metadata import apply_case_metadata


ROOT = Path(__file__).resolve().parents[1]
UI_PROJECTS = ROOT / "auto_tests" / "ui"


def test_apply_case_metadata_sets_complete_allure_hierarchy(monkeypatch):
    recorded: list[tuple[str, str]] = []

    def record(name):
        return lambda value: recorded.append((name, value))

    monkeypatch.setattr("allure.dynamic.id", record("id"))
    monkeypatch.setattr("allure.dynamic.epic", record("epic"))
    monkeypatch.setattr("allure.dynamic.feature", record("feature"))
    monkeypatch.setattr("allure.dynamic.story", record("story"))
    monkeypatch.setattr("allure.dynamic.title", record("title"))

    apply_case_metadata(
        case_id="PYTEST-UI-ID-001",
        title="定位导航元素",
        epic="Mango Mock UI 自动化",
        feature="UI 元素定位",
        story="全局导航",
    )

    assert recorded == [
        ("id", "PYTEST-UI-ID-001"),
        ("epic", "Mango Mock UI 自动化"),
        ("feature", "UI 元素定位"),
        ("story", "全局导航"),
        ("title", "PYTEST-UI-ID-001 定位导航元素"),
    ]


@pytest.mark.parametrize(
    ("case_id", "title"),
    [("001", "正常标题"), ("bad-id", "正常标题"), ("UI-001", "test_raw_name")],
)
def test_apply_case_metadata_rejects_unreadable_cases(case_id, title):
    with pytest.raises(ValueError):
        apply_case_metadata(
            case_id=case_id,
            title=title,
            epic="项目",
            feature="模块",
        )


def test_ui_capabilities_are_split_by_module_and_use_global_metadata():
    expected_counts = {
        "operations": (12, "apply_operation_case_metadata"),
        "interactions": (5, "apply_element_case_metadata"),
        "inventory": (8, "apply_inventory_case_metadata"),
    }
    for project in ("simple_ui", "pytest_ui"):
        capability_dir = UI_PROJECTS / project / "test_cases" / "capabilities"
        for group, (expected_count, helper) in expected_counts.items():
            files = sorted((capability_dir / group).glob("test_*.py"))
            assert len(files) == expected_count
            assert all(helper in file.read_text(encoding="utf-8") for file in files)

    assert not (UI_PROJECTS / "simple_ui" / "test_cases" / "test_excel_ui_cases.py").exists()
    assert not (UI_PROJECTS / "pytest_ui" / "test_cases" / "test_mango_mock_ui.py").exists()


def test_bdd_bindings_are_one_feature_per_file():
    binding_root = UI_PROJECTS / "bdd_ui" / "test_cases"
    bindings = sorted((binding_root / "business").glob("test_*.py"))
    bindings += sorted((binding_root / "capabilities").rglob("test_*.py"))
    assert len(bindings) == 28
    for path in bindings:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        scenario_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"scenario", "scenarios"}
        ]
        assert len(scenario_calls) == 1, path
        function_name = scenario_calls[0].func.id
        assert len(scenario_calls[0].args) == (2 if function_name == "scenario" else 1), path
        feature_path = scenario_calls[0].args[0]
        assert isinstance(feature_path, ast.Constant), path
        assert Path(feature_path.value).stem == path.stem.removeprefix("test_"), path


def test_bdd_aggregate_binding_files_are_forbidden():
    test_cases = UI_PROJECTS / "bdd_ui" / "test_cases"
    assert not (test_cases / "test_business_bdd.py").exists()
    assert not (test_cases / "test_capabilities_bdd.py").exists()


def test_bdd_hook_maps_capability_and_business_metadata(monkeypatch):
    bdd_conftest = import_module("auto_tests.ui.bdd_ui.conftest")
    operation = bdd_conftest.OPERATION_CASES[0]
    capability_calls = []
    monkeypatch.setattr(
        bdd_conftest,
        "apply_operation_case_metadata",
        lambda case, **metadata: capability_calls.append((case, metadata)),
    )
    capability_request = SimpleNamespace(
        node=SimpleNamespace(
            callspec=SimpleNamespace(
                params={"case_id": operation.case_id}
            )
        )
    )
    bdd_conftest.pytest_bdd_before_scenario(
        capability_request,
        SimpleNamespace(name="框架操作能力"),
        SimpleNamespace(name="参数化场景"),
    )
    assert capability_calls == [(operation, {"category": "clicks"})]

    business_calls = []
    monkeypatch.setattr(
        bdd_conftest,
        "apply_case_metadata",
        lambda **metadata: business_calls.append(metadata),
    )
    business_request = SimpleNamespace(node=SimpleNamespace(callspec=None))
    bdd_conftest.pytest_bdd_before_scenario(
        business_request,
        SimpleNamespace(name="订单业务"),
        SimpleNamespace(name="BDD-UI-ORDER-001 创建并查询订单"),
    )
    assert business_calls[0]["case_id"] == "BDD-UI-ORDER-001"
    assert business_calls[0]["feature"] == "订单业务"
    assert business_calls[0]["title"] == "创建并查询订单"


def test_simple_ui_has_no_ignored_legacy_cases():
    test_cases = UI_PROJECTS / "simple_ui" / "test_cases"
    assert not list(test_cases.glob("test_*.py"))
    assert "collect_ignore" not in (test_cases / "conftest.py").read_text(encoding="utf-8")
    abstract = UI_PROJECTS / "simple_ui" / "abstract"
    assert {path.name for path in abstract.glob("*.py")} == {
        "__init__.py",
        "excel_case_page.py",
    }
