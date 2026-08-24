from mangoautomation.enums import ElementExpEnum, ElementOperationEnum
from mangoautomation.models import MethodModel

from auto_tests.ui.bdd_ui.config.settings import BddUIMockConfig
from auto_tests.ui.pytest_ui.config.settings import PytestUIMockConfig
from auto_tests.ui.simple_ui.config.settings import MockUIConfig
from core.sources.element_schema import CANONICAL_ELEMENT_HEADERS
from core.sources.feishu.document_data import DocumentData
from core.sources.ui_elements import load_ui_element_records
from core.ui import configured_element_repository
from core.ui.element_runtime import ElementDefinition


def _record(**overrides):
    value = {
        "ID": 7,
        "项目名称": "MockUI服务",
        "模块名称": "components",
        "页面名称": "componentsPage",
        "元素名称": "submit-button",
        "元素分类": "表单操作",
        "AI自愈状态": "是",
        "采集快照": "是",
        "定位方式1": "TEST_ID",
        "定位表达式1": "submit-button",
        "元素下标1": 0,
        "是否iframe1": "否",
        "AI定位提示词1": "提交表单按钮",
    }
    value.update(overrides)
    return value


def test_chinese_element_row_maps_to_mangoautomation_models():
    definition = ElementDefinition.from_record(_record())
    model = definition.to_element_model(
        operation_type=ElementOperationEnum.OPE,
        method="w_click",
        arguments=[MethodModel(f="locating")],
    )

    assert model.element_id == 7
    assert model.category == "表单操作"
    assert model.ai_heal_status == 1
    assert model.collect_snapshot is True
    assert model.elements[0].exp == ElementExpEnum.LOCATOR.value
    assert model.elements[0].loc == "get_by_test_id('submit-button')"
    assert model.elements[0].sub == 1
    assert model.elements[0].prompt == "提交表单按钮"


def test_legacy_and_feishu_headers_remain_compatible():
    definition = ElementDefinition.from_record({
        "ID": 8,
        "项目名称": "MockUI服务",
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
    import pandas as pd

    source = pd.DataFrame([{
        "ID": 1,
        "*元素名称": "login-button",
        "*类型-1": "TEST_ID",
        "*定位-1": "login-button",
    }])
    normalized = DocumentData._canonical_element_columns(source)

    assert normalized.loc[0, "元素名称"] == "login-button"
    assert normalized.loc[0, "定位方式1"] == "TEST_ID"
    assert normalized.loc[0, "定位表达式1"] == "login-button"
    assert normalized.loc[0, "AI自愈状态"] == "是"
    assert list(normalized.columns) == list(CANONICAL_ELEMENT_HEADERS)


def test_legacy_feishu_sheet_maps_third_locator_by_column_position():
    import pandas as pd

    headers = [
        "ID", "项目名称", "模块名称", "页面名称", "元素名称",
        "定位方式1", "表达式1", "下标1", "定位方式2", "表达式2",
        "下标2", "定位方式3", "表达式2", "下标3", "AI提示词", "等待",
    ]
    source = pd.DataFrame([[
        1, "MockUI服务", "认证", "登录", "登录按钮",
        "TEST_ID", "login", 0, "CSS", "#login", 1,
        "XPATH", "//button", 2, "查找登录按钮", 3,
    ]], columns=headers)

    normalized = DocumentData._canonical_element_columns(source)

    assert list(normalized.columns) == list(CANONICAL_ELEMENT_HEADERS)
    assert normalized.loc[0, "定位表达式3"] == "//button"
    assert normalized.loc[0, "等待时间"] == 3


def test_excel_element_products_are_loaded_from_core_sources():
    records = load_ui_element_records(
        source="excel",
        project="mock_ui",
        product_name="MockUI服务",
    )
    assert len(records) == 260
    assert records[0]["项目名称"] == "MockUI服务"


def test_each_ui_project_declares_its_element_source_product():
    configurations = (
        MockUIConfig(),
        BddUIMockConfig(),
        PytestUIMockConfig(),
    )

    for settings in configurations:
        assert settings.ELEMENT_SOURCE == "excel"
        assert settings.ELEMENT_PROJECT == "mock_ui"
        assert settings.ELEMENT_PRODUCT == "MockUI服务"


def test_ui_projects_share_the_core_element_repository():
    settings = BddUIMockConfig()

    first = configured_element_repository(settings)
    second = configured_element_repository(settings)

    assert first is second
    assert len(first.all()) == 260
    definition = first.all()[0]
    assert first.get(
        definition.name,
        module_name=definition.module_name,
        page_name=definition.page_name,
    ) == definition


def test_core_element_repository_supports_page_scope():
    settings = MockUIConfig()
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
    import pandas as pd
    import core.sources.ui_elements as sources

    class FakeDocumentData:
        def ui_element(self):
            return pd.DataFrame([_record()])

    sources.load_ui_element_records.cache_clear()
    monkeypatch.setattr(sources, "DocumentData", FakeDocumentData)

    records = sources.load_ui_element_records(
        source="feishu",
        project="mock_ui",
        product_name="MockUI服务",
    )

    assert len(records) == 1
    assert records[0]["元素名称"] == "submit-button"
    sources.load_ui_element_records.cache_clear()
