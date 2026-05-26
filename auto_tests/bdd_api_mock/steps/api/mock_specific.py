# -*- coding: utf-8 -*-
"""Mock API 项目专用 BDD 步骤。"""

import csv
import os
from typing import Dict

from pytest_bdd import given, then, parsers

from core.utils import log


SYSTEM_HEADER_KEYS = ("X-Custom-Key", "X-Request-Source")


def _clear_system_headers(api_client):
    for key in SYSTEM_HEADER_KEYS:
        api_client.headers.pop(key, None)


@given(parsers.parse("已设置正确系统自定义请求头"))
def set_valid_system_headers(api_client):
    """设置 /health、/info 所需的自定义请求头。"""
    api_client.headers.update(
        {
            "X-Custom-Key": "mango_secret_key",
            "X-Request-Source": "bdd_api_mock",
        }
    )
    log.debug("已设置正确系统自定义请求头")


@given(parsers.parse("未设置系统自定义请求头"))
def clear_system_headers(api_client):
    """清理 /health、/info 的自定义请求头，避免跨场景泄漏。"""
    _clear_system_headers(api_client)
    log.debug("已清理系统自定义请求头")


@given(parsers.parse("已设置错误系统自定义密钥"))
def set_invalid_system_key(api_client):
    """设置错误的 X-Custom-Key。"""
    api_client.headers.update(
        {
            "X-Custom-Key": "wrong_key",
            "X-Request-Source": "bdd_api_mock",
        }
    )
    log.debug("已设置错误系统自定义密钥")


@then(parsers.parse("下载CSV文件应该包含3列5行数据"))
def downloaded_csv_should_have_three_columns_and_five_rows(api_response: Dict):
    """验证 /download/excel 生成的 CSV 文件结构。"""
    response = api_response["response"]
    file_path = getattr(response, "file_path", None) or response.data

    assert file_path, "响应中没有下载文件路径"
    assert os.path.exists(file_path), f"下载文件不存在: {file_path}"

    with open(file_path, "r", encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.reader(csv_file))

    assert len(rows) == 6, f"期望1行表头+5行数据，实际 {len(rows)} 行"
    header = [cell.lstrip("\ufeff") for cell in rows[0]]
    assert header == ["姓名", "年龄", "城市"], f"CSV表头不正确: {rows[0]}"
    for index, row in enumerate(rows[1:], start=1):
        assert len(row) == 3, f"第 {index} 行期望3列，实际 {len(row)} 列"
