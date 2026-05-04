# -*- coding: utf-8 -*-
"""
带实体引用的 API 请求步骤

提供使用实体 ID 的 HTTP 请求步骤
"""

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


def _get_entity_from_fixture(created_entity):
    """从 fixture 字典中提取实体对象"""
    if isinstance(created_entity, dict):
        return created_entity.get("entity")
    return created_entity


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+GET\s+"(?P<path>[^"]+)"'),
)
def api_get_with_entity_step(
    entity_name: str, path: str, api_client, created_entity, api_response
):
    """使用实体ID的 GET 请求步骤"""
    entity = _get_entity_from_fixture(created_entity)
    
    # 构建 context 用于占位符替换
    context = {}
    if entity and hasattr(entity, "id"):
        entity_key = _get_entity_key(entity_name)
        context[f"{entity_key}.id"] = entity.id
    
    result = api_client.request("GET", path, context=context)
    api_response.clear()
    api_response["response"] = result


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+POST\s+"(?P<path>[^"]+)"\s*:'),
)
def api_post_with_entity_step(
    entity_name: str,
    path: str,
    docstring,
    api_client,
    created_entity,
    api_response,
):
    """使用实体ID的 POST 请求步骤"""
    entity = _get_entity_from_fixture(created_entity)

    # 构建 context 用于占位符替换
    context = {}
    if entity and hasattr(entity, "id"):
        entity_key = _get_entity_key(entity_name)
        context[f"{entity_key}.id"] = entity.id

    # 将 docstring 作为原始字符串传递给 client，由 client 处理占位符替换和 JSON 解析
    result = api_client.request("POST", path, json_data=docstring, context=context)
    api_response.clear()
    api_response["response"] = result


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+PUT\s+"(?P<path>[^"]+)"\s*:'),
)
def api_put_with_entity_step(
    entity_name: str,
    path: str,
    docstring,
    api_client,
    created_entity,
    api_response,
):
    """使用实体ID的 PUT 请求步骤"""
    entity = _get_entity_from_fixture(created_entity)
    
    # 构建 context 用于占位符替换
    context = {}
    if entity and hasattr(entity, "id"):
        entity_key = _get_entity_key(entity_name)
        context[f"{entity_key}.id"] = entity.id

    # 将 docstring 作为原始字符串传递给 client，由 client 处理占位符替换和 JSON 解析
    result = api_client.request("PUT", path, json_data=docstring, context=context)
    api_response.clear()
    api_response["response"] = result


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+DELETE\s+"(?P<path>[^"]+)"'),
)
def api_delete_with_entity_step(
    entity_name: str, path: str, api_client, created_entity, api_response
):
    """使用实体ID的 DELETE 请求步骤"""
    entity = _get_entity_from_fixture(created_entity)
    
    # 构建 context 用于占位符替换
    context = {}
    if entity and hasattr(entity, "id"):
        entity_key = _get_entity_key(entity_name)
        context[f"{entity_key}.id"] = entity.id
    
    result = api_client.request("DELETE", path, context=context)
    api_response.clear()
    api_response["response"] = result
