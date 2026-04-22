# -*- coding: utf-8 -*-
"""
API 调用步骤 - 参考 bdd_api_ucai 架构

提供通用的 API 请求步骤，支持认证和数据占位符替换
"""

import json
import re
from typing import Any, Dict, Optional

from pytest_bdd import given, when, parsers

# 从 api_client 模块导入 APIClient
from auto_tests.bdd_api_mock.api_client import APIClient


# ==================== 通用 API 步骤（使用 mock_api_client）====================


@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"'), target_fixture="api_response")
def api_get_step(path: str, mock_api_client):
    """GET 请求步骤 - 使用已认证的客户端"""
    return mock_api_client.get(path)


@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"\s*:'), target_fixture="api_response")
def api_get_with_params_step(path: str, docstring, mock_api_client):
    """GET 请求步骤（带参数）"""
    params = json.loads(docstring) if docstring else {}
    return mock_api_client.get(path, params=params)


@when(parsers.re(r'POST\s+"(?P<path>[^"]+)"\s*:'), target_fixture="api_response")
def api_post_step(path: str, docstring, mock_api_client):
    """POST 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    return mock_api_client.post(path, body)


@when(parsers.re(r'PUT\s+"(?P<path>[^"]+)"\s*:'), target_fixture="api_response")
def api_put_step(path: str, docstring, mock_api_client):
    """PUT 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    return mock_api_client.put(path, body)


@when(parsers.re(r'DELETE\s+"(?P<path>[^"]+)"'), target_fixture="api_response")
def api_delete_step(path: str, mock_api_client):
    """DELETE 请求步骤"""
    return mock_api_client.delete(path)


# ==================== 带实体引用的 API 步骤 ====================


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+GET\s+"(?P<path>[^"]+)"'),
    target_fixture="api_response",
)
def api_get_with_entity_step(
    entity_name: str, path: str, mock_api_client, created_entity
):
    """使用实体ID的 GET 请求步骤"""
    return mock_api_client.get(path, created_entity=created_entity)


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+POST\s+"(?P<path>[^"]+)"\s*:'),
    target_fixture="api_response",
)
def api_post_with_entity_step(
    entity_name: str, path: str, docstring, mock_api_client, created_entity
):
    """使用实体ID的 POST 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    return mock_api_client.post(path, body, created_entity=created_entity)


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+PUT\s+"(?P<path>[^"]+)"\s*:'),
    target_fixture="api_response",
)
def api_put_with_entity_step(
    entity_name: str, path: str, docstring, mock_api_client, created_entity
):
    """使用实体ID的 PUT 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    return mock_api_client.put(path, body, created_entity=created_entity)


@when(
    parsers.re(r'使用(?P<entity_name>\w+)ID\s+DELETE\s+"(?P<path>[^"]+)"'),
    target_fixture="api_response",
)
def api_delete_with_entity_step(
    entity_name: str, path: str, mock_api_client, created_entity
):
    """使用实体ID的 DELETE 请求步骤"""
    return mock_api_client.delete(path, created_entity=created_entity)
