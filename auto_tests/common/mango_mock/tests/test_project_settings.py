"""Demo 项目的元素源和控制台参数注册约定。"""

from auto_tests.ui.bdd_ui.config.settings import BddUIMockConfig
from auto_tests.ui.pytest_ui.config.settings import PytestUIMockConfig
from auto_tests.ui.simple_ui.config.settings import MockUIConfig


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



def test_console_no_longer_declares_credential_or_dead_healing_mode_option() -> None:
    """控制台不得再暴露凭据输入，也不得暴露在 2.1.0 下无效的自愈模式。"""

    from auto_tests.project_registry import UI_RUNTIME_OPTIONS

    keys = {option["key"] for option in UI_RUNTIME_OPTIONS}
    assert "AI_API_KEY" not in keys
    assert "ELEMENT_HEALING_MODE" not in keys
    assert {"AI_ELEMENT_HEALING_ENABLED", "AI_BASE_URL", "AI_MODEL"} <= keys
