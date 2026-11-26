"""
DAL 统一断言步骤 — 测试 conftest

提供 api_response 和 data fixtures，覆盖新旧两套步骤体系。
"""
import json
import pytest
from pytest_bdd import given, when, then, parsers
from core.dal import expect
from core.dal.assertion_steps import *  # noqa: F401, F403 — 加载统一断言步骤


# ============================================================
# 测试上下文
# ============================================================

class TestContext:
    def __init__(self):
        self.data = None
        self.last_result = None
        self.last_error = None


@pytest.fixture
def ctx():
    return TestContext()


# ============================================================
# api_response mock
# ============================================================

@pytest.fixture
def api_response():
    return {}


class MockResponse:
    def __init__(self, status_code: int, data: dict):
        self.status_code = status_code
        self.data = data


@given(parsers.parse('模拟API响应状态码{code:d}'), target_fixture="api_response")
def mock_api_response(code: int):
    """创建模拟 API 响应"""
    return {"response": MockResponse(code, {})}


@given('模拟响应体:')
def mock_response_body(api_response, docstring: str):
    """设置模拟响应的 body"""
    import textwrap
    text = textwrap.dedent(docstring)
    api_response["response"].data = json.loads(text)


# ============================================================
# data fixture（供新步骤使用）
# ============================================================

@given(parsers.parse('准备数据:'), target_fixture='data')
def prepare_data(docstring: str):
    import textwrap
    return json.loads(textwrap.dedent(docstring))


@given(parsers.parse('准备列表数据:'), target_fixture='data')
def prepare_list_data(docstring: str):
    import textwrap
    return json.loads(textwrap.dedent(docstring))


# ============================================================
# 旧测试兼容（test_data fixture）
# ============================================================

@given(parsers.parse('数据为:'), target_fixture='test_data')
def given_data_legacy(ctx, docstring: str):
    ctx.data = json.loads(docstring)
    return ctx.data


@given(parsers.parse('列表数据为:'), target_fixture='list_data')
def given_list_data_legacy(ctx, docstring: str):
    ctx.data = json.loads(docstring)
    return ctx.data


@given(parsers.parse('存在表格数据:'), target_fixture='table_data')
def given_table_data_legacy(ctx, docstring: str):
    lines = [line.strip() for line in docstring.strip().split('\n')]
    headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
    rows = []
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        row = {}
        for i, header in enumerate(headers):
            if i < len(cells):
                try:
                    row[header] = float(cells[i]) if '.' in cells[i] else int(cells[i])
                except ValueError:
                    row[header] = cells[i]
        rows.append(row)
    ctx.data = rows
    return ctx.data


@when(parsers.parse('使用 DAL 表达式验证 "{expression}"'))
def when_validate_expression_legacy(ctx, expression: str):
    ctx.expression = expression
    try:
        expect(ctx.data).should(expression)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@when(parsers.parse('使用 DAL 表达式验证:'))
def when_validate_multiline_legacy(ctx, docstring: str):
    ctx.expression = docstring.strip()
    try:
        expect(ctx.data).should(docstring)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@when(parsers.parse('验证列表:'))
def when_validate_list_legacy(ctx, docstring: str):
    ctx.expression = docstring.strip()
    try:
        expect(ctx.data).should(docstring)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@then(parsers.parse('验证应该通过'))
def then_should_pass_legacy(ctx):
    assert ctx.last_result is True, f"验证失败: {ctx.last_error}"


@then(parsers.parse('验证应该失败'))
def then_should_fail_legacy(ctx):
    assert ctx.last_result is False, "预期验证失败，但实际通过了"


@then(parsers.parse('错误信息应该包含 "{text}"'))
def then_error_should_contain_legacy(ctx, text: str):
    assert text in ctx.last_error, f"错误信息不包含 '{text}': {ctx.last_error}"


# ============================================================
# 新测试用验证步骤
# ============================================================

@when(parsers.parse('执行断言"{expression}"'))
def execute_assertion(ctx, data, expression: str):
    ctx.expression = expression
    try:
        expect(data).should(expression)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@then('断言应该通过')
def assertion_should_pass(ctx):
    assert ctx.last_result is True, f"断言失败: {ctx.last_error}"


@then('断言应该失败')
def assertion_should_fail(ctx):
    assert ctx.last_result is False, "期望断言失败但通过了"
