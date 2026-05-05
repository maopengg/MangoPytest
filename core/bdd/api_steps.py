# -*- coding: utf-8 -*-
"""
通用 API 请求步骤定义

提供跨项目可用的 BDD 步骤：
- GET/POST/PUT/DELETE 请求
- 支持占位符替换
- 支持命名实体引用
- 支持自定义请求头

使用方法:
    1. 在项目 conftest.py 中导入:
       from core.bdd.api_steps import *
    
    2. 提供 api_client fixture
"""

import json
from typing import Any, Dict, Optional

import pytest
from pytest_bdd import when, parsers, given

from core.bdd.context import EntityContext
from core.bdd.placeholder import PlaceholderReplacer, parse_json_with_placeholders
from core.utils import log


# 存储 API 响应的 fixture
@pytest.fixture
def api_response() -> Dict[str, Any]:
    """API 响应存储 fixture"""
    return {}


# 自定义请求头 fixture
@pytest.fixture
def custom_headers() -> Dict[str, str]:
    """自定义请求头 fixture（默认空）"""
    return {}


@given(parsers.parse('设置请求头:'), target_fixture="custom_headers")
def set_custom_headers_step(table):
    """设置自定义请求头
    
    示例:
        假如 设置请求头:
          | 字段名   | 值        |
          | deadde   | 21312321  |
          | X-Sign   | abc123    |
    """
    headers = {}
    for row in table:
        headers[row['字段名']] = row['值']
    
    log.debug(f"设置自定义请求头: {headers}")
    return headers


@when(parsers.parse('GET "{path}"'))
def api_get_step(
    path: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """GET 请求
    
    示例:
        当 GET "/users"
        当 GET "/users/${{user.id}}"
        当 GET "/users/@user.id"
    """
    # 替换 URL 中的占位符
    replacer = PlaceholderReplacer(
        entity_context.build_placeholder_context(path)
    )
    resolved_path = replacer.replace(path)
    
    log.debug(f"GET {resolved_path}")
    
    result = api_client.request("GET", resolved_path, headers=custom_headers)
    api_response.clear()
    api_response["response"] = result
    
    log.info(f"GET {resolved_path} -> {result.status_code}")
    return result


@when(parsers.parse('POST "{path}":'))
def api_post_step(
    path: str,
    docstring: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """POST 请求，支持 JSON 请求体中的占位符
    
    示例:
        当 POST "/orders":
          请求体中的 product_id 会被替换为实体的 id
    """
    # 替换 URL 中的占位符
    replacer = PlaceholderReplacer(
        entity_context.build_placeholder_context(path)
    )
    resolved_path = replacer.replace(path)
    
    # 解析并替换请求体中的占位符
    body = parse_json_with_placeholders(docstring, entity_context)
    
    log.debug(f"POST {resolved_path} body={body}")
    
    result = api_client.request("POST", resolved_path, json_data=body, headers=custom_headers)
    api_response.clear()
    api_response["response"] = result
    
    log.info(f"POST {resolved_path} -> {result.status_code}")
    return result


@when(parsers.parse('PUT "{path}":'))
def api_put_step(
    path: str,
    docstring: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """PUT 请求，支持 JSON 请求体中的占位符
    
    示例:
        当 PUT "/orders/${{order.id}}":
          请求体中的字段会被替换
    """
    # 替换 URL 中的占位符
    replacer = PlaceholderReplacer(
        entity_context.build_placeholder_context(path)
    )
    resolved_path = replacer.replace(path)
    
    # 解析并替换请求体中的占位符
    body = parse_json_with_placeholders(docstring, entity_context)
    
    log.debug(f"PUT {resolved_path} body={body}")
    
    result = api_client.request("PUT", resolved_path, json_data=body, headers=custom_headers)
    api_response.clear()
    api_response["response"] = result
    
    log.info(f"PUT {resolved_path} -> {result.status_code}")
    return result


@when(parsers.parse('DELETE "{path}"'))
def api_delete_step(
    path: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """DELETE 请求
    
    示例:
        当 DELETE "/orders/${{order.id}}"
    """
    # 替换 URL 中的占位符
    replacer = PlaceholderReplacer(
        entity_context.build_placeholder_context(path)
    )
    resolved_path = replacer.replace(path)
    
    log.debug(f"DELETE {resolved_path}")
    
    result = api_client.request("DELETE", resolved_path, headers=custom_headers)
    api_response.clear()
    api_response["response"] = result
    
    log.info(f"DELETE {resolved_path} -> {result.status_code}")
    return result


@when(parsers.parse('使用 @{alias} 发送 {method} 到 "{path}":'))
def api_request_with_entity_step(
    alias: str,
    method: str,
    path: str,
    docstring: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """使用指定实体作为上下文发送请求
    
    支持 attr 简写格式，自动引用指定实体的属性
    
    示例:
        当使用 @产品 发送 POST 到 "/orders":
          请求体中可以使用 id, name 等属性
    """
    # 获取指定实体
    entity = entity_context.get(alias)
    
    # 构建上下文，支持 attr 简写
    context = entity_context.build_placeholder_context(docstring)
    
    # 添加简写格式 attr -> entity.attr
    for attr in dir(entity):
        if not attr.startswith('_'):
            value = getattr(entity, attr)
            if not callable(value):
                context[f"{{{{{attr}}}}}"] = value
    
    # 替换 URL
    replacer = PlaceholderReplacer(context)
    resolved_path = replacer.replace(path)
    
    # 替换请求体
    body = parse_json_with_placeholders(docstring, entity_context)
    
    log.debug(f"{method} {resolved_path} with @{alias}")
    
    result = api_client.request(method.upper(), resolved_path, json_data=body, headers=custom_headers)
    api_response.clear()
    api_response["response"] = result
    
    log.info(f"{method} {resolved_path} -> {result.status_code}")
    return result
