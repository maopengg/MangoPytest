"""新版 bdd_ui 只注册本项目独立 Steps 与 Fixtures。"""

from auto_tests.ui.bdd_ui.cases import ELEMENT_CASES, OPERATION_CASES

pytest_plugins = [
    "auto_tests.ui.bdd_ui.fixtures.bdd",
    "auto_tests.ui.bdd_ui.steps.mango_mock_steps",
    "auto_tests.ui.bdd_ui.steps.business_steps",
    "auto_tests.ui.bdd_ui.hooks.artifacts",
]


def pytest_collection_modifyitems(items):
    """把能力矩阵的优先级转换为可选择的 pytest marks。"""
    priorities = {case.case_id: case.priority.lower() for case in OPERATION_CASES}
    risk_priority = {"高": "p0", "中": "p1", "低": "p2"}
    priorities.update(
        {case.case_id: risk_priority[case.risk] for case in ELEMENT_CASES}
    )
    for item in items:
        callspec = getattr(item, "callspec", None)
        example = callspec.params.get("_pytest_bdd_example", {}) if callspec else {}
        case_id = example.get("case_id")
        if case_id in priorities:
            item.add_marker(priorities[case_id])
