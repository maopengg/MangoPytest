"""公共 Case 元数据的组装及输入校验。"""

import pytest
from core.execution.case_metadata import apply_case_metadata


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
        case_id="UI-ID-001",
        title="定位导航元素",
        epic="示例产品",
        feature="UI 元素定位",
        story="全局导航",
    )

    assert recorded == [
        ("id", "UI-ID-001"),
        ("epic", "示例产品"),
        ("feature", "UI 元素定位"),
        ("story", "全局导航"),
        ("title", "UI-ID-001 定位导航元素"),
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
