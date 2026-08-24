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
        "定位方式1": "TEST_ID",
        "定位表达式1": "submit-button",
        "元素下标1": 0,
        "AI定位提示词1": "提交表单按钮",
        "定位方式2": "CSS",
        "定位表达式2": "#submit-button",
        "AI定位提示词2": "表单底部的提交按钮",
        "定位方式3": "XPATH",
        "定位表达式3": "//button[@data-testid='submit-button']",
        "AI定位提示词3": "文本为提交的主按钮",
        "说明": "提交当前表单",
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
    assert model.category == "componentsPage"
    assert model.ai_heal_status == 0
    assert model.collect_snapshot is False
    assert len(model.elements) == 3
    assert model.elements[0].exp == ElementExpEnum.LOCATOR.value
    assert model.elements[0].loc == "get_by_test_id('submit-button')"
    assert model.elements[0].sub == 1
    assert model.elements[0].is_iframe is None
    assert model.elements[0].prompt == "提交表单按钮"
    assert model.elements[1].prompt == "表单底部的提交按钮"
    assert model.elements[2].prompt == "文本为提交的主按钮"
    assert definition.description == "提交当前表单"


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
    assert normalized.loc[0, "AI定位提示词1"] is None
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
    assert normalized.loc[0, "AI定位提示词1"] == "查找登录按钮"


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


def test_ai_healing_defaults_are_centralized_in_system_settings():
    from core.settings import settings as system_settings

    config = MockUIConfig()
    assert config.ELEMENT_HEALING_ENABLED == system_settings.ELEMENT_HEALING_ENABLED
    assert config.AI_ELEMENT_HEALING_ENABLED == system_settings.AI_ELEMENT_HEALING_ENABLED
    assert config.AI_BASE_URL == system_settings.AI_BASE_URL
    assert config.AI_MODEL == system_settings.AI_MODEL
    assert config.AI_TIMEOUT == system_settings.AI_TIMEOUT
    assert config.AI_SEMANTIC_STRENGTH == system_settings.AI_SEMANTIC_STRENGTH


def test_runtime_passes_ai_settings_to_healing_harness(monkeypatch):
    from importlib import import_module

    runtime_module = import_module("core.ui.element_runtime")

    captured = {}

    class FakeHarness:
        @staticmethod
        def standalone(**kwargs):
            captured.update(kwargs)
            return "healing-engine"

    class FakeBaseData:
        locator_engine = None
        log = "logger"
        is_ai = False

        def set_locator_engine(self, engine):
            self.locator_engine = engine

    class Settings:
        ELEMENT_HEALING_ENABLED = True
        ELEMENT_HEALING_MODE = 3
        AI_ELEMENT_HEALING_ENABLED = True
        AI_API_KEY = "test-key"
        AI_BASE_URL = "https://ai.example/v1"
        AI_MODEL = "test-model"
        AI_TIMEOUT = 45
        AI_SEMANTIC_STRENGTH = 70

    monkeypatch.setattr(runtime_module, "WebElementHealingHarness", FakeHarness)
    runtime = runtime_module.ElementRuntime.__new__(runtime_module.ElementRuntime)
    runtime.base_data = FakeBaseData()
    runtime._configure_healing(Settings())

    assert runtime.base_data.locator_engine == "healing-engine"
    assert runtime.base_data.is_ai is True
    assert captured == {
        "api_key": "test-key",
        "base_url": "https://ai.example/v1",
        "model": "test-model",
        "timeout": 45,
        "mode": 3,
        "semantic_strength": 70,
        "logger": "logger",
    }


def test_named_element_reuses_actual_operation_step(monkeypatch):
    from contextlib import contextmanager
    from importlib import import_module

    from mangotools.enums import StatusEnum

    runtime_module = import_module("core.ui.element_runtime")
    definition = ElementDefinition.from_record(_record())
    attachments = []
    steps = []

    @contextmanager
    def fake_step(name):
        steps.append(name)
        yield

    class FakeResult:
        status = StatusEnum.SUCCESS.value
        error_message = None

        @staticmethod
        def model_dump(mode="json"):
            return {"status": StatusEnum.SUCCESS.value, "locator_engine": {"used_ai": False}}

    class FakeDriver:
        def __init__(self, base_data):
            self.base_data = base_data

        def w_click(self, locating):
            return None

        def element_main(self, model):
            context = self.base_data._ui_operation_evidence_context
            context["input"] = {
                "operation": "w_click",
                "arguments": [{"element_reference": "element-1"}],
                "keyword_arguments": {},
                "elements": [{"reference": "element-1", "match_count": 1}],
            }
            return FakeResult()

    class FakeRepository:
        @staticmethod
        def get(name):
            assert name == "submit-button"
            return definition

    class FakePage:
        url = "http://mock.local/"

    class FakeBaseData:
        page = FakePage()
        ui_element_results = []

    base_data = FakeBaseData()
    runtime = runtime_module.ElementRuntime.__new__(runtime_module.ElementRuntime)
    runtime.base_data = base_data
    runtime.repository = FakeRepository()
    runtime.driver = FakeDriver(base_data)
    runtime.last_result = None
    monkeypatch.setattr(runtime_module.allure, "step", fake_step)
    monkeypatch.setattr(
        runtime_module,
        "attach_json",
        lambda name, value: attachments.append((name, value)),
    )

    runtime.execute("submit-button", "w_click")

    assert steps == ["UI 操作 · w_click · submit-button"]
    assert [name for name, _ in attachments] == ["操作信息", "操作结果"]
    operation_input = attachments[0][1]
    assert operation_input["named_elements"][0]["name"] == "submit-button"
    assert operation_input["named_elements"][0]["project_name"] == "MockUI服务"
    assert operation_input["named_elements"][0]["locators"][0] == {
        "slot": 1,
        "method": "TEST_ID",
        "expression": "submit-button",
        "index": 0,
        "ai_prompt": "提交表单按钮",
    }
    assert attachments[1][1]["status"] == "passed"
    assert not hasattr(base_data, "_ui_operation_evidence_context")


def test_evidence_plugin_captures_locator_without_nested_step(monkeypatch):
    from importlib import import_module

    plugin = import_module("core.execution.pytest_evidence_plugin")

    class FakeFirst:
        @staticmethod
        def evaluate(script, timeout):
            return {"tag_name": "button", "attributes": {"data-testid": "submit-button"}}

    class FakeLocator:
        first = FakeFirst()

        @staticmethod
        def count():
            return 1

    class FakeBaseData:
        _ui_operation_evidence_context = {"method": "w_click", "input": None}

    class FakeOwner:
        def __init__(self):
            self.base_data = FakeBaseData()
            self.clicked = False

        def w_click(self, locating):
            self.clicked = True

    plugin._patch_method(FakeOwner, "w_click")
    monkeypatch.setattr(
        plugin.allure,
        "step",
        lambda name: (_ for _ in ()).throw(AssertionError("不应创建嵌套步骤")),
    )
    owner = FakeOwner()

    owner.w_click(FakeLocator())

    assert owner.clicked is True
    operation_input = owner.base_data._ui_operation_evidence_context["input"]
    assert operation_input["operation"] == "w_click"
    assert operation_input["elements"][0]["match_count"] == 1


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
