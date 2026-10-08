"""元素表 AI 定位提示词的数据契约（三列合并 + 体检规则）。

其中若干用例直接调用 mangoautomation 的解析函数，把「写法 → 实际被 AI 读到的
内容」固化成回归证明：排除项位置写错时，语义会**反转**成正向必需文本。
"""

import pytest

from core.sources.prompt_spec import (
    ERROR,
    PROMPT_COLUMNS,
    WARNING,
    lint_prompt,
    lint_records,
    merge_prompt_columns,
    positive_prompt_lines,
    summarize,
)


def rules(issues) -> set[str]:
    return {issue.rule for issue in issues}


def levels(issues) -> dict[str, int]:
    return summarize(issues)


# ------------------------------------------------------------------ 三列合并


def test_merge_joins_three_columns_with_newlines() -> None:
    merged = merge_prompt_columns({
        "AI定位提示词1": "位于文件上传区域的文件上传输入框",
        "AI定位提示词2": "位于「组件演示」页的组件面板内",
        "AI定位提示词3": "排除项：下载按钮",
    })
    assert merged == (
        "位于文件上传区域的文件上传输入框\n"
        "位于「组件演示」页的组件面板内\n"
        "排除项：下载按钮"
    )


def test_merge_is_backward_compatible_with_single_column() -> None:
    assert merge_prompt_columns({
        "AI定位提示词1": "位于顶部导航栏的按钮",
        "AI定位提示词2": None,
        "AI定位提示词3": "",
    }) == "位于顶部导航栏的按钮"


def test_merge_drops_blank_lines_and_supports_legacy_alias() -> None:
    assert merge_prompt_columns({
        "AI定位提示词1": "  第一行  \n\n  第二行  \n",
    }) == "第一行\n第二行"
    # 旧飞书表只有 AI定位提示词 一列
    assert merge_prompt_columns({"AI定位提示词": "旧列提示词"}) == "旧列提示词"
    assert merge_prompt_columns({"提示词": "别名提示词"}) == "别名提示词"
    assert merge_prompt_columns({column: None for column in PROMPT_COLUMNS}) is None


def test_positive_prompt_lines_drops_exclusion_lines() -> None:
    merged = "第一行描述\n排除项：不要这个\n第二行描述"
    assert positive_prompt_lines(merged) == ["第一行描述", "第二行描述"]


# ------------------------------------------------------------------ 错误级规则


def test_exclusion_must_start_its_own_line() -> None:
    """排除项写在句中会被库侧当成正向必需文本，语义反转——必须报错。"""

    issue_list = lint_prompt(
        element_id=1, element_name="ui-file-input",
        columns=["位于文件上传区域的选择框，排除项：下载按钮", None, None],
        has_locator=True,
    )
    assert "exclusion_not_at_line_start" in rules(issue_list)
    assert next(i for i in issue_list if i.rule == "exclusion_not_at_line_start").is_error


def test_exclusion_on_its_own_line_is_accepted() -> None:
    issue_list = lint_prompt(
        element_id=1, element_name="ui-file-input",
        columns=["位于文件上传区域的文件上传输入框", None, "排除项：下载按钮"],
        has_locator=True,
    )
    assert "exclusion_not_at_line_start" not in rules(issue_list)
    assert levels(issue_list)[ERROR] == 0


def test_exclusion_only_prompt_is_an_error() -> None:
    issue_list = lint_prompt(
        element_id=1, element_name="ui-file-input",
        columns=[None, None, "排除项：下载按钮"],
        has_locator=True,
    )
    assert "exclusion_only" in rules(issue_list)


def test_runtime_variable_must_be_declared() -> None:
    """未声明的 ${{变量}} 会让元素初始化直接失败，与 AI 开关无关。"""

    issue_list = lint_prompt(
        element_id=1, element_name="order-idempotency-key",
        columns=["位于订单表单、显示「${{idem_key}}」的文本输入框", None, None],
        has_locator=True,
    )
    assert "undefined_prompt_variable" in rules(issue_list)

    allowed = lint_prompt(
        element_id=1, element_name="order-idempotency-key",
        columns=["位于订单表单、显示「${{idem_key}}」的文本输入框", None, None],
        has_locator=True,
        allowed_variables={"idem_key"},
    )
    assert "undefined_prompt_variable" not in rules(allowed)


# ------------------------------------------------------------------ 警告级规则


def test_template_prompt_is_flagged() -> None:
    issue_list = lint_prompt(
        element_id=1, element_name="ui-file-input",
        columns=["查找元素：ui-file-input", None, None],
        has_locator=True,
    )
    assert {"template_prompt", "prompt_equals_element_name"} <= rules(issue_list)
    assert levels(issue_list)[ERROR] == 0


def test_missing_prompt_is_a_warning_only_when_element_has_locator() -> None:
    with_locator = lint_prompt(
        element_id=1, element_name="ui-file-input", columns=[None, None, None],
        has_locator=True,
    )
    without_locator = lint_prompt(
        element_id=1, element_name="ui-file-input", columns=[None, None, None],
        has_locator=False,
    )
    assert rules(with_locator) == {"missing_prompt"}
    assert without_locator == []


def test_control_keyword_hint_only_applies_to_interactive_elements() -> None:
    interactive = lint_prompt(
        element_id=1, element_name="create-order",
        columns=["位于订单业务区的主要动作", None, None], has_locator=True,
    )
    display = lint_prompt(
        element_id=2, element_name="history-result",
        columns=["位于浏览器与页签区、显示历史状态的文本", None, None], has_locator=True,
    )
    assert "missing_control_keyword" in rules(interactive)
    assert "missing_control_keyword" not in rules(display)


def test_lint_records_reports_all_problem_elements() -> None:
    issues = lint_records([
        {"ID": 1, "元素名称": "create-order", "定位方式1": "TEST_ID",
         "定位表达式1": "create-order", "AI定位提示词1": "查找元素：create-order"},
        {"ID": 2, "元素名称": "history-result", "定位方式1": "TEST_ID",
         "定位表达式1": "history-result",
         "AI定位提示词1": "位于浏览器与页签区、显示「history-0」的状态文本"},
    ])
    assert {issue.element_id for issue in issues} == {1}
    assert all(issue.level == WARNING for issue in issues)


# ------------------------------------------ 与内部包解析行为的一致性（回归证明）


def test_library_parsers_confirm_exclusion_inversion() -> None:
    """实证：排除项不在行首时会被当成正向必需文本。"""

    sanitizer = pytest.importorskip(
        "mangoautomation.element_healing.context.sanitizer"
    )
    from mangoautomation.enums import ElementOperationEnum
    from mangoautomation.models import ElementListModel, ElementModel

    def required_texts(prompt: str) -> list[str]:
        model = ElementModel(
            id=1, element_id=1, type=ElementOperationEnum.OPE, name="ui-file-input",
            ope_key="w_click", sleep=0,
            elements=[ElementListModel(
                exp=2, loc="get_by_test_id('ui-file-input')", prompt=prompt,
            )],
        )
        return sanitizer.semantic_required_texts(model)

    # 正确写法：排除项独占一行 → 被剔除，不进入必需文本
    correct = required_texts(
        "位于文件上传区域、显示「选择文件」的按钮\n排除项：下载按钮"
    )
    assert "选择文件" in correct
    assert "下载按钮" not in correct

    # 错误写法：排除项夹在句中 → 语义反转，变成必须命中的目标
    inverted = required_texts("位于文件上传区域的选择框，排除项：下载按钮")
    assert "下载按钮" in inverted

    # 正确写法下 positive_prompt 会剔除排除项行
    assert sanitizer.positive_prompt("描述行\n排除项：下载按钮") == "描述行"
