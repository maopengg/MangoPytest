"""临时 Excel、飞书记录及元素仓库的公共数据源契约。"""

import pytest
from mangoautomation.enums import ElementExpEnum
from core.ui.element_runtime import ElementDefinition
from core.sources.element_schema import CANONICAL_ELEMENT_HEADERS
from core.sources.feishu.document_data import DocumentData
from core.sources.ui_elements import load_ui_element_records
from core.ui import configured_element_repository
from .records import element_record as _record
from .records import SampleUIConfig

pytestmark = pytest.mark.usefixtures("element_workbook")


def test_legacy_and_feishu_headers_remain_compatible():
    definition = ElementDefinition.from_record({
        "ID": 8,
        "项目名称": "框架测试产品",
        "模块名称": "legacy",
        "页面名称": "legacyPage",
        "*元素名称": "legacy-button",
        "*类型-1": "CSS",
        "*定位-1": "#legacy",
        "元素下标-1": 1,
    })

    locator = definition.locators[0].to_model()
    assert definition.name == "legacy-button"
    assert locator.exp == ElementExpEnum.CSS.value
    assert locator.loc == "#legacy"
    assert locator.sub == 2


def test_feishu_columns_are_normalized_to_canonical_names():
    source_record = {
        "ID": 1,
        "*元素名称": "login-button",
        "*类型-1": "TEST_ID",
        "*定位-1": "login-button",
    }
    source = [list(source_record), list(source_record.values())]
    normalized = DocumentData._canonical_element_columns(source)

    assert normalized[0]["元素名称"] == "login-button"
    assert normalized[0]["定位方式1"] == "TEST_ID"
    assert normalized[0]["定位表达式1"] == "login-button"
    assert normalized[0]["AI定位提示词1"] is None
    assert list(normalized[0]) == list(CANONICAL_ELEMENT_HEADERS)


def test_legacy_feishu_sheet_maps_third_locator_by_column_position():
    headers = [
        "ID", "项目名称", "模块名称", "页面名称", "元素名称",
        "定位方式1", "表达式1", "下标1", "定位方式2", "表达式2",
        "下标2", "定位方式3", "表达式2", "下标3", "AI提示词", "等待",
    ]
    source = [headers, [
        1, "框架测试产品", "认证", "登录", "登录按钮",
        "TEST_ID", "login", 0, "CSS", "#login", 1,
        "XPATH", "//button", 2, "查找登录按钮", 3,
    ]]

    normalized = DocumentData._canonical_element_columns(source)

    assert list(normalized[0]) == list(CANONICAL_ELEMENT_HEADERS)
    assert normalized[0]["定位表达式3"] == "//button"
    assert normalized[0]["AI定位提示词1"] == "查找登录按钮"


def test_feishu_sparse_rows_preserve_canonical_column_priority():
    normalized = DocumentData._canonical_element_columns([
        ["ID", "元素名称", "*元素名称", "定位方式1", "定位表达式1"],
        [1, "canonical-name", "legacy-name"],
    ])

    assert normalized[0]["元素名称"] == "canonical-name"
    assert normalized[0]["定位表达式1"] is None


def test_feishu_duplicate_ids_across_sheets_are_rejected():
    from types import SimpleNamespace
    import pytest
    from core.exceptions import ToolsError

    document = object.__new__(DocumentData)
    document.config = SimpleNamespace(surface=SimpleNamespace(ui_element_id="sheet-token"))
    document.url = "https://example.invalid/"
    document.parameter = ""
    document.get_sheet = lambda token: [{"sheet_id": "first"}, {"sheet_id": "second"}]
    document.cls = lambda url: [["ID", "元素名称"], [1, "repeated-id"]]

    with pytest.raises(ToolsError):
        document.ui_element()


def test_canonical_schema_only_contains_pytest_ui_element_fields():
    assert len(CANONICAL_ELEMENT_HEADERS) == 18
    assert CANONICAL_ELEMENT_HEADERS[:5] == (
        "ID", "项目名称", "模块名称", "页面名称", "元素名称"
    )
    for slot in range(1, 4):
        assert f"定位方式{slot}" in CANONICAL_ELEMENT_HEADERS
        assert f"定位表达式{slot}" in CANONICAL_ELEMENT_HEADERS
        assert f"元素下标{slot}" in CANONICAL_ELEMENT_HEADERS
        assert f"AI定位提示词{slot}" in CANONICAL_ELEMENT_HEADERS
    assert {"AI自愈状态", "采集快照", "等待时间", "是否iframe1"}.isdisjoint(
        CANONICAL_ELEMENT_HEADERS
    )


def test_excel_element_products_are_loaded_from_core_sources():
    records = load_ui_element_records(
        source="excel",
        project="sample_ui",
        product_name="框架测试产品",
    )
    assert len(records) == 3
    assert records[0]["项目名称"] == "框架测试产品"


def test_ui_projects_share_the_core_element_repository():
    settings = SampleUIConfig()

    first = configured_element_repository(settings)
    second = configured_element_repository(settings)

    assert first is second
    assert len(first.all()) == 3
    definition = first.all()[0]
    assert first.get(
        definition.name,
        module_name=definition.module_name,
        page_name=definition.page_name,
    ) == definition


def test_core_element_repository_supports_page_scope():
    settings = SampleUIConfig()
    all_elements = configured_element_repository(settings)
    expected = all_elements.all()[0]

    scoped = configured_element_repository(
        settings,
        module_name=expected.module_name,
        page_name=expected.page_name,
    )

    assert scoped.get(expected.name) == expected
    assert all(
        item.module_name == expected.module_name
        and item.page_name == expected.page_name
        for item in scoped.all()
    )


def test_feishu_source_is_selected_by_the_same_setting(monkeypatch):
    import core.sources.ui_elements as sources

    class FakeDocumentData:
        def ui_element(self):
            return [_record()]

    sources.load_ui_element_records.cache_clear()
    monkeypatch.setattr(sources, "DocumentData", FakeDocumentData)

    records = sources.load_ui_element_records(
        source="feishu",
        project="sample_ui",
        product_name="框架测试产品",
    )

    assert len(records) == 1
    assert records[0]["元素名称"] == "submit-button"
    sources.load_ui_element_records.cache_clear()
