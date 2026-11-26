"""独立于业务项目的 UI 样例配置与元素记录。"""

from core.ui.config import UIRuntimeConfig


class SampleUIConfig(UIRuntimeConfig):
    ELEMENT_PROJECT: str = "sample_ui"
    ELEMENT_PRODUCT: str = "框架测试产品"
    ARTIFACT_DIR: str = "reports/ui-tests"


def element_record(**overrides):
    value = {
        "ID": 7,
        "项目名称": "框架测试产品",
        "模块名称": "components",
        "页面名称": "formPage",
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
