# -*- coding: utf-8 -*-
"""
DAL 统一断言步骤

所有断言统一走 DAL 引擎。步骤文本采用紧凑中文格式（引号前后无空格）。

架构：
  API 测试 → 响应应该为: → api_response 展平为 {status_code, body} → DAL 断言
  路径步骤 → "path"应该为"value" → 拼装 DAL 表达式 → expect(data).should(expr)
  通用步骤 → 数据应该匹配: → 直接 DAL 断言

Feature 文件规范（紧凑格式）：
  那么 响应状态码应该为200
  那么 响应字段"code"应该为"200"
  那么 "body.data.size"应该大于0
  那么 数据应该匹配:
    \"\"\"
    name = 张三
    \"\"\"

  那么 响应应该为:
    \"\"\"
    : { status_code: 200, body.code: 200 }
    \"\"\"
"""

import textwrap
from typing import Any, Dict

from pytest_bdd import then, parsers

from core.dal import expect
from core.models.api import APIResponse
from core.utils import log


def _extract(data: Any, path: str) -> Any:
    """从 data 中按点分隔路径提取值"""
    parts = path.replace("[", ".[").split(".")
    current = data
    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            idx = int(part[1:-1])
            if isinstance(current, list) and idx < len(current):
                current = current[idx]
            else:
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _eval_multiline(actual: Any, docstring: str):
    """去除 Gherkin docstring 缩进并逐行执行 DAL 断言"""
    text = textwrap.dedent(docstring).strip()
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        log.debug(f"DAL: {line}")
        expect(actual).should(line)


# ============================================================
# 辅助
# ============================================================

def _response_data(api_response: Dict) -> Dict:
    resp: APIResponse = api_response["response"]
    return {
        "status_code": resp.status_code,
        "body": resp.data if isinstance(resp.data, dict) else {},
    }



# ============================================================
# 桥接步骤：api_response → data
# ============================================================

@then('API响应作为断言数据', target_fixture="data")
def api_response_to_data(api_response: Dict):
    """将 api_response 的 body 提取为 data fixture，供路径断言步骤使用。

    Feature 示例:
        当 用户查询合同列表
        那么 API响应作为断言数据
        那么 "code"应该为200
        那么 "success"应该为true
    """
    if isinstance(api_response, dict):
        return api_response.get("data", api_response)
    return api_response.data


# ============================================================
# 主入口 — TestCharm 风格
# ============================================================

@then(parsers.parse('响应应该为:'))
def response_should_be(api_response: Dict, docstring: str):
    """
    统一 API 响应断言。将 api_response 展平为 {status_code, body} 后执行 DAL。

    示例:
        那么 响应应该为:
          \"\"\"
          : { status_code: 200, body.code: 200, body.success: true }
          \"\"\"
    """
    data = _response_data(api_response)
    _eval_multiline(data, docstring)
    log.info("DAL 断言通过")


@then(parsers.parse('响应体应该为:'))
def response_body_should_be(api_response: Dict, docstring: str):
    """直接对响应 body 做 DAL 断言（不含 status_code）。"""
    body = _response_data(api_response)["body"]
    _eval_multiline(body, docstring)
    log.info("DAL body 断言通过")


# ============================================================
# 通用 DAL — 操作 data fixture
# ============================================================

@then(parsers.parse('数据应该匹配:'))
def data_should_match(data: Any, docstring: str):
    """通用 DAL 多行断言，直接对 data fixture 执行。"""
    _eval_multiline(data, docstring)
    log.info("DAL 数据断言通过")


@then(parsers.parse('数据应该匹配表格:'))
def data_should_match_table(data: Any, docstring: str):
    """DAL 表格断言。"""
    text = textwrap.dedent(docstring).strip()
    expect(data).should(text)
    log.info("DAL 表格断言通过")


# ============================================================
# 路径断言 — 操作 data fixture（紧凑模式：引号与中文之间无空格）
# ============================================================

@then(parsers.parse('"{path}"应该为"{value}"'))
def path_should_equal(data: Any, path: str, value: str):
    expect(data).should(f"{path} = '{value}'")


@then(parsers.parse('"{path}"应该为{value:d}'))
def path_should_equal_int(data: Any, path: str, value: int):
    expect(data).should(f"{path} = {value}")


@then(parsers.parse('"{path}"应该存在'))
def path_should_exist(data: Any, path: str):
    expect(data).should(f"{path} is NotNull")


@then(parsers.parse('"{path}"不应该为空'))
def path_should_not_be_empty(data: Any, path: str):
    expect(data).should(f"{path}.size > 0")


@then(parsers.parse('"{path}"应该包含"{value}"'))
def path_should_contain(data: Any, path: str, value: str):
    expect(data).should(f"{path} contains '{value}'")


@then(parsers.parse('"{path}"应该匹配"{pattern}"'))
def path_should_match(data: Any, path: str, pattern: str):
    expect(data).should(f"{path} = /{pattern}/")


@then(parsers.parse('"{path}"大小应该为{size:d}'))
def path_size_should_equal(data: Any, path: str, size: int):
    expect(data).should(f"{path}.size = {size}")


@then(parsers.parse('"{path}"大小应该大于{size:d}'))
def path_size_should_gt(data: Any, path: str, size: int):
    expect(data).should(f"{path}.size > {size}")


@then(parsers.parse('"{path}"应该大于{value:d}'))
def path_should_gt(data: Any, path: str, value: int):
    expect(data).should(f"{path} > {value}")


@then(parsers.parse('"{path}"应该为true'))
def path_should_be_true(data: Any, path: str):
    expect(data).should(f"{path} = true")


@then(parsers.parse('"{path}"应该为false'))
def path_should_be_false(data: Any, path: str):
    expect(data).should(f"{path} = false")


# ============================================================
# api_response 便捷步骤
# ============================================================

@then(parsers.parse('响应状态码应该为{code:d}'))
def status_code_should_be(code: int, api_response: Dict):
    data = _response_data(api_response)
    expect(data).should(f"status_code = {code}")


@then(parsers.parse('响应字段"{field}"应该为"{value}"'))
def response_field_should_equal(field: str, value: str, api_response: Dict):
    body = _response_data(api_response)["body"]
    actual = str(body.get(field, ""))
    expect(actual).should(f"= '{value}'")


@then(parsers.parse('响应消息应该包含"{text}"'))
def response_message_should_contain(text: str, api_response: Dict):
    body = _response_data(api_response)["body"]
    msg = body.get("message", "") if isinstance(body, dict) else ""
    expect(msg).should(f"contains '{text}'")


# ============================================================
# 列表/集合
# ============================================================

@then(parsers.parse('列表长度应该为{length:d}'))
def list_length_should_be(length: int, data: Any):
    expect(data).should(f".size = {length}")


@then(parsers.parse('列表长度应该大于等于{length:d}'))
def list_length_should_be_gte(length: int, data: Any):
    expect(data).should(f".size >= {length}")


# ============================================================
# 异步等待
# ============================================================

@then(parsers.parse('最终"{path}"应该为"{value}"'))
def eventually_path_should_equal(data: Any, path: str, value: str):
    expect(data).should(f"::eventually {path} = '{value}'")


@then(parsers.parse('最终"{path}"应该为{value:d}'))
def eventually_path_should_equal_int(data: Any, path: str, value: int):
    expect(data).should(f"::eventually {path} = {value}")




