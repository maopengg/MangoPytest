# -*- coding: utf-8 -*-
"""
带实体引用的 API 请求步骤

提供使用实体 ID 的 HTTP 请求步骤
"""

import json
from typing import Any, Dict, Optional

from pytest_bdd import when, parsers


def _get_entity_from_fixture(created_entity):
    """从 fixture 字典中提取实体对象"""
    if isinstance(created_entity, dict):
        return created_entity.get("entity")
    return created_entity


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+GET\s+"(?P<path>[^"]+)"'),
)
def api_get_with_entity_step(
    entity_name: str, path: str, mock_api_client, created_entity, api_response
):
    """使用实体ID的 GET 请求步骤"""
    entity = _get_entity_from_fixture(created_entity)
    result = mock_api_client.get(path, created_entity=entity)
    api_response.clear()
    api_response.update(result)


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+POST\s+"(?P<path>[^"]+)"\s*:'),
)
def api_post_with_entity_step(
    entity_name: str,
    path: str,
    docstring,
    mock_api_client,
    created_entity,
    api_response,
):
    """使用实体ID的 POST 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    entity = _get_entity_from_fixture(created_entity)

    # 根据实体名称自动添加相应的 ID 字段
    if entity and hasattr(entity, "id"):
        entity_id = entity.id
        if entity_name == "报销":
            body["reimbursement_id"] = entity_id
        elif entity_name == "部门审批":
            body["dept_approval_id"] = entity_id
        elif entity_name == "财务审批":
            body["finance_approval_id"] = entity_id
        elif entity_name == "用户":
            body["user_id"] = entity_id
        elif entity_name == "产品":
            body["product_id"] = entity_id
        elif entity_name == "订单":
            body["order_id"] = entity_id

    result = mock_api_client.post(path, body, created_entity=entity)
    api_response.clear()
    api_response.update(result)


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+PUT\s+"(?P<path>[^"]+)"\s*:'),
)
def api_put_with_entity_step(
    entity_name: str,
    path: str,
    docstring,
    mock_api_client,
    created_entity,
    api_response,
):
    """使用实体ID的 PUT 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    entity = _get_entity_from_fixture(created_entity)
    result = mock_api_client.put(path, body, created_entity=entity)
    api_response.clear()
    api_response.update(result)


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+DELETE\s+"(?P<path>[^"]+)"'),
)
def api_delete_with_entity_step(
    entity_name: str, path: str, mock_api_client, created_entity, api_response
):
    """使用实体ID的 DELETE 请求步骤"""
    entity = _get_entity_from_fixture(created_entity)
    result = mock_api_client.delete(path, created_entity=entity)
    api_response.clear()
    api_response.update(result)
