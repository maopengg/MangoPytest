"""
pytest-bdd step definitions for DAL tests
"""
import json
import pytest
from pytest_bdd import given, when, then, parsers
from core.dal import expect


class TestContext:
    """测试上下文"""
    def __init__(self):
        self.data = None
        self.expression = None
        self.last_result = None
        self.last_error = None


@pytest.fixture
def ctx():
    """创建测试上下文"""
    return TestContext()


@given(parsers.parse('数据为:'), target_fixture='test_data')
def given_data(ctx, docstring):
    """解析测试数据"""
    ctx.data = json.loads(docstring)
    return ctx.data


@given(parsers.parse('列表数据为:'), target_fixture='list_data')
def given_list_data(ctx, docstring):
    """解析列表数据"""
    ctx.data = json.loads(docstring)
    return ctx.data


@given(parsers.parse('存在表格数据:'), target_fixture='table_data')
def given_table_data(ctx, docstring):
    """解析表格数据"""
    lines = [line.strip() for line in docstring.strip().split('\n')]
    headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
    rows = []
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        row = {}
        for i, header in enumerate(headers):
            if i < len(cells):
                # 尝试解析为数字
                try:
                    if '.' in cells[i]:
                        row[header] = float(cells[i])
                    else:
                        row[header] = int(cells[i])
                except ValueError:
                    row[header] = cells[i]
        rows.append(row)
    ctx.data = rows
    return ctx.data


@when(parsers.parse('使用 DAL 表达式验证 "{expression}"'))
def when_validate_expression(ctx, expression):
    """验证简单表达式"""
    ctx.expression = expression
    try:
        expect(ctx.data).should(expression)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@when(parsers.parse('使用 DAL 表达式验证:'))
def when_validate_multiline_expression(ctx, docstring):
    """验证多行表达式"""
    ctx.expression = docstring.strip()
    try:
        expect(ctx.data).should(docstring)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@when(parsers.parse('验证列表:'))
def when_validate_list(ctx, docstring):
    """验证列表"""
    ctx.expression = docstring.strip()
    try:
        expect(ctx.data).should(docstring)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@then(parsers.parse('验证应该通过'))
def then_validation_should_pass(ctx):
    """验证应该成功"""
    assert ctx.last_result is True, f"验证失败: {ctx.last_error}"


@then(parsers.parse('验证应该失败'))
def then_validation_should_fail(ctx):
    """验证应该失败"""
    assert ctx.last_result is False, "预期验证失败，但实际通过了"


@then(parsers.parse('错误信息应该包含 "{text}"'))
def then_error_should_contain(ctx, text):
    """错误信息应该包含指定文本"""
    assert text in ctx.last_error, f"错误信息不包含 '{text}': {ctx.last_error}"
