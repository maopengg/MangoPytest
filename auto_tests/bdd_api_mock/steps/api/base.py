# -*- coding: utf-8 -*-
"""
基础 API 请求步骤

提供通用的 HTTP 请求步骤（GET, POST, PUT, DELETE）
"""

import json
from typing import Any, Dict

from pytest_bdd import when, parsers


@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"'))
def api_get_step(path: str, mock_api_client, api_response):
    """GET 请求步骤 - 使用已认证的客户端"""
    result = mock_api_client.get(path)
    # 将结果存储到 api_response fixture
    api_response.clear()
    api_response.update(result)


@when(parsers.re(r'GET\s+"(?P<path>[^"]+)"\s*:'))
def api_get_with_params_step(path: str, docstring, mock_api_client, api_response):
    """GET 请求步骤（带参数）"""
    params = json.loads(docstring) if docstring else {}
    result = mock_api_client.get(path, params=params)
    api_response.clear()
    api_response.update(result)


@when(parsers.parse('带参数 GET "{path}":\n{params_table}'))
def api_get_with_table_params_step(
    path: str, params_table: str, mock_api_client, api_response
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
    result = mock_api_client.get(path, params=params)
    api_response.clear()
    api_response.update(result)


@when(parsers.re(r'POST\s+"(?P<path>[^"]+)"\s*:'))
def api_post_step(path: str, docstring, mock_api_client, api_response):
    """POST 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    result = mock_api_client.post(path, body)
    api_response.clear()
    api_response.update(result)


@when(parsers.re(r'PUT\s+"(?P<path>[^"]+)"\s*:'))
def api_put_step(path: str, docstring, mock_api_client, api_response):
    """PUT 请求步骤"""
    body = json.loads(docstring) if docstring else {}
    result = mock_api_client.put(path, body)
    api_response.clear()
    api_response.update(result)


@when(parsers.re(r'DELETE\s+"(?P<path>[^"]+)"'))
def api_delete_step(path: str, mock_api_client, api_response):
    """DELETE 请求步骤"""
    result = mock_api_client.delete(path)
    api_response.clear()
    api_response.update(result)
