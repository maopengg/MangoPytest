# -*- coding: utf-8 -*-
"""
基础 API 请求步骤

提供通用的 HTTP 请求步骤（GET, POST, PUT, DELETE）
"""

import json

from pytest_bdd import when, parsers


# 实体名称到占位符 key 的映射
ENTITY_NAME_TO_KEY = {
    "用户": "user",
    "产品": "product",
    "订单": "order",
    "数据": "data",
    "文件": "file",
    "报销": "reimbursement",
    "部门审批": "deptapproval",
    "财务审批": "financeapproval",
    "总经理审批": "ceoapproval",
    "认证": "auth",
    "API日志": "apilog",
    "健康状态": "health",
}


def _get_entity_key(entity_name: str) -> str:
    """获取实体对应的占位符 key"""
    return ENTITY_NAME_TO_KEY.get(entity_name, entity_name.lower())


@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"'))
def api_get_step(path: str, api_client, api_response):
    """GET 请求步骤 - 使用已认证的客户端"""
    result = api_client.request("GET", path)
    # 直接存储 APIResponse 对象
    api_response.clear()
    api_response["response"] = result


@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"\s*:'))
def api_get_with_params_step(path: str, docstring, api_client, api_response):
    """GET 请求步骤（带参数）"""
    params = json.loads(docstring) if docstring else {}
    result = api_client.request("GET", path, params=params)
    api_response.clear()
    api_response["response"] = result


@when(parsers.parse('带参数 GET "{path}":\n{params_table}'))
def api_get_with_table_params_step(
    path: str, params_table: str, api_client, api_response
):
    """GET 请求步骤（带表格参数）"""
    # 解析表格参数
    lines = params_table.strip().split("\n")
    if len(lines) >= 2:
        # 第一行是表头，第二行是值
        headers = [h.strip() for h in lines[0].split("|") if h.strip()]
        values = [v.strip() for v in lines[1].split("|") if v.strip()]
        params = dict(zip(headers, values))
    else:
        params = {}
    result = api_client.request("GET", path, params=params)
    api_response.clear()
    api_response["response"] = result


@when(parsers.re(r'POST\s+"(?P<path>[^"]+)"\s*:'))
def api_post_step(path: str, docstring, api_client, api_response, created_entity):
    """POST 请求步骤

    支持在请求体中使用 ${{entity.id}} 占位符，会从 created_entity 中替换
    """
    # 构建 context 用于占位符替换
    context = {}
    if created_entity and "entity" in created_entity:
        entity = created_entity["entity"]
        entity_name = created_entity.get("entity_name", "")
        entity_key = _get_entity_key(entity_name)
        context[f"{entity_key}.id"] = entity.id

    # 将 docstring 作为原始字符串传递给 client，由 client 处理占位符替换
    result = api_client.request("POST", path, json_data=docstring, context=context)
    api_response.clear()
    api_response["response"] = result


@when(parsers.re(r'PUT\s+"(?P<path>[^"]+)"\s*:'))
def api_put_step(path: str, docstring, api_client, api_response, created_entity):
    """PUT 请求步骤

    支持在请求体中使用 ${{entity.id}} 占位符，会从 created_entity 中替换
    """
    # 构建 context 用于占位符替换
    context = {}
    if created_entity and "entity" in created_entity:
        entity = created_entity["entity"]
        entity_name = created_entity.get("entity_name", "")
        entity_key = _get_entity_key(entity_name)
        context[f"{entity_key}.id"] = entity.id

    # 将 docstring 作为原始字符串传递给 client，由 client 处理占位符替换
    result = api_client.request("PUT", path, json_data=docstring, context=context)
    api_response.clear()
    api_response["response"] = result


@when(parsers.re(r'DELETE\s+"(?P<path>[^"]+)"'))
def api_delete_step(path: str, api_client, api_response):
    """DELETE 请求步骤"""
    result = api_client.request("DELETE", path)
    api_response.clear()
    api_response["response"] = result
