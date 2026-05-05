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


@when(parsers.parse('GET "{path}" 预期失败'))
def api_get_expect_fail_step(
    path: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """GET 请求（预期失败，捕获异常）
    
    示例:
        当 GET "/users" 预期失败
    """
    from core.exceptions import ApiError
    
    # 替换 URL 中的占位符
    replacer = PlaceholderReplacer(
        entity_context.build_placeholder_context(path)
    )
    resolved_path = replacer.replace(path)
    
    log.debug(f"GET {resolved_path} (预期失败)")
    
    try:
        result = api_client.request("GET", resolved_path, headers=custom_headers)
        api_response.clear()
        api_response["response"] = result
        log.info(f"GET {resolved_path} -> {result.status_code}")
        return result
    except ApiError as e:
        # 捕获 API 异常，将错误信息包装成响应格式
        log.debug(f"GET {resolved_path} 失败: {e.code}")
        api_response.clear()
        api_response["response"] = e
        api_response["status_code"] = e.code
        return e


@when(parsers.parse('POST "{path}" 预期失败'))
def api_post_expect_fail_step(
    path: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """POST 请求（预期失败，捕获异常）
    
    示例:
        当 POST "/upload" 预期失败
    """
    from core.exceptions import ApiError
    
    # 替换 URL 中的占位符
    replacer = PlaceholderReplacer(
        entity_context.build_placeholder_context(path)
    )
    resolved_path = replacer.replace(path)
    
    log.debug(f"POST {resolved_path} (预期失败)")
    
    try:
        result = api_client.request("POST", resolved_path, headers=custom_headers)
        api_response.clear()
        api_response["response"] = result
        log.info(f"POST {resolved_path} -> {result.status_code}")
        return result
    except ApiError as e:
        # 捕获 API 异常，将错误信息包装成响应格式
        log.debug(f"POST {resolved_path} 失败: {e.code}")
        api_response.clear()
        api_response["response"] = e
        api_response["status_code"] = e.code
        return e


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


@when(
    parsers.parse('上传文件 "{file_path}" 到 "{endpoint}"'),
    target_fixture="api_response",
)
def upload_file_step(
    file_path: str,
    endpoint: str,
    api_client,
    api_response: Dict,
):
    """上传文件步骤
    
    示例:
        当 上传文件 "data/uploads/test.txt" 到 "/upload"
    """
    import os
    from pathlib import Path
    
    # 构建完整文件路径 - 从项目根目录开始
    base_dir = Path(__file__).parent.parent.parent
    full_path = base_dir / "auto_tests" / "bdd_api_mock" / file_path
    
    log.debug(f"上传文件: {full_path}")
    
    if not full_path.exists():
        raise FileNotFoundError(f"文件不存在: {full_path}")
    
    # 读取文件内容
    with open(full_path, "rb") as f:
        file_content = f.read()
    
    # 构建 multipart 请求
    import mimetypes
    content_type, _ = mimetypes.guess_type(str(full_path))
    if content_type is None:
        content_type = "application/octet-stream"
    
    filename = full_path.name
    
    # 使用 api_client 发送 multipart 请求
    files = {"file": (filename, file_content, content_type)}
    
    result = api_client.request(
        "POST",
        endpoint,
        files=files,
    )
    api_response.clear()
    api_response["response"] = result
    api_response["status_code"] = result.status_code
    api_response["data"] = result.data if hasattr(result, 'data') else {}
    
    log.info(f"上传文件 {filename} -> {result.status_code}")
    return api_response


@when(parsers.parse('使用Authorization头发送 {method} 到 "{path}"'))
def api_request_with_auth_header_step(
    method: str,
    path: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
):
    """使用 Authorization 头发送请求
    
    示例:
        当 使用Authorization头发送 GET 到 "/users"
    """
    # 替换 URL 中的占位符
    replacer = PlaceholderReplacer(
        entity_context.build_placeholder_context(path)
    )
    resolved_path = replacer.replace(path)
    
    log.debug(f"{method} {resolved_path} 使用 Authorization 头")
    
    # 使用当前 api_client 的 token，通过 Authorization 头发送
    # 这里假设 api_client 已经设置了正确的 token
    result = api_client.request(method.upper(), resolved_path)
    api_response.clear()
    api_response["response"] = result
    api_response["status_code"] = result.status_code
    api_response["data"] = result.data if hasattr(result, 'data') else {}
    
    log.info(f"{method} {resolved_path} -> {result.status_code}")
    return api_response


@when(parsers.parse('保存响应字段 "{field}" 到 "{alias}"'))
def save_response_field_step(
    field: str,
    alias: str,
    api_response: Dict,
    entity_context: EntityContext,
):
    """保存响应中的字段值到上下文
    
    示例:
        当 保存响应字段 "data.id" 到 "部门审批"
        当 保存响应字段 "id" 到 "部门审批"
    """
    response = api_response.get("response")
    if not response:
        raise ValueError("没有可用的响应数据")
    
    # 获取响应数据 - APIResponse 的 data 属性就是响应体字典
    response_data = getattr(response, 'data', None)
    if response_data is None:
        response_data = api_response.get("data", {})
    
    # 确保 response_data 是字典
    if not isinstance(response_data, dict):
        raise ValueError(f"响应数据不是字典类型: {type(response_data)}")
    
    # 解析字段路径（支持 data.id 或 id 格式）
    # API 响应格式是 {"code": 200, "message": "...", "data": {"id": 123, ...}}
    # 所以 "data.id" 实际上是指 response.data.data.id
    # 而 "id" 是指 response.data.data.id (简写)
    
    # 获取内层的 data 字段（业务数据）
    business_data = response_data.get('data', {})
    if not isinstance(business_data, dict):
        raise ValueError(f"业务数据不是字典类型: {type(business_data)}")
    
    # 如果字段以 "data." 开头，从 business_data 中获取
    if field.startswith("data."):
        field_name = field[5:]  # 去掉 "data." 前缀
    else:
        # 简写格式，直接使用字段名
        field_name = field
    
    # 获取字段值
    value = business_data.get(field_name)
    if value is None:
        raise ValueError(f"响应中不存在字段: {field} (可用字段: {list(business_data.keys())})")
    
    # 创建一个简单的对象来存储值
    class SimpleEntity:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    entity = SimpleEntity(value=value, **{field_name: value})
    entity_context.add(alias, entity)
    
    log.debug(f"保存响应字段 {field}={value} 到 @{alias}")
    return api_response


@when(parsers.parse('使用 @{entity_alias} 和 @{context_alias} 发送 {method} 到 "{path}":'))
def api_request_with_entity_and_context_step(
    entity_alias: str,
    context_alias: str,
    method: str,
    path: str,
    docstring: str,
    api_client,
    api_response: Dict,
    entity_context: EntityContext,
    custom_headers: Dict = None,
):
    """使用指定实体和上下文数据发送请求
    
    支持从上下文别名获取数据，并在请求体中使用
    
    示例:
        当 使用 @报销 和 @部门审批 发送 POST 到 "/finance-approvals":
          请求体中可以使用 {{部门审批.id}} 或 @部门审批.id
    """
    # 获取指定实体
    entity = entity_context.get(entity_alias)
    context_entity = entity_context.get(context_alias)
    
    # 构建上下文，支持 attr 简写
    context = entity_context.build_placeholder_context(docstring)
    
    # 添加实体简写格式 attr -> entity.attr
    for attr in dir(entity):
        if not attr.startswith('_'):
            value = getattr(entity, attr)
            if not callable(value):
                context[f"{{{{{attr}}}}}"] = value
    
    # 添加上下文实体数据
    for attr in dir(context_entity):
        if not attr.startswith('_'):
            value = getattr(context_entity, attr)
            if not callable(value):
                context[f"{{{{{context_alias}.{attr}}}}}"] = value
                context[f"@{context_alias}.{attr}"] = value
    
    # 替换 URL
    replacer = PlaceholderReplacer(context)
    resolved_path = replacer.replace(path)
    
    # 替换请求体
    body = parse_json_with_placeholders(docstring, entity_context)
    
    # 手动替换 body 中的上下文引用
    import json
    body_str = json.dumps(body)
    body_str = replacer.replace(body_str)
    body = json.loads(body_str)
    
    log.debug(f"{method} {resolved_path} with @{entity_alias} + @{context_alias}")
    
    result = api_client.request(method.upper(), resolved_path, json_data=body, headers=custom_headers)
    api_response.clear()
    api_response["response"] = result
    
    log.info(f"{method} {resolved_path} -> {result.status_code}")
    return result
