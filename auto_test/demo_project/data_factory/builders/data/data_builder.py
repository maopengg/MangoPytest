# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据构造器 - 对应 /api/data 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, Optional
import uuid

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("data")
class DataBuilder(BaseBuilder):
    """
    数据构造器
    对应 /api/data 接口 (POST)
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)

    def build(self, name: str = None, value: int = None) -> Dict[str, Any]:
        """
        构造数据（不调用API）
        @return: 数据字典
        """
        return {
            "name": name or f"data_{uuid.uuid4().hex[:6]}",
            "value": value or 100
        }

    def submit(self, name: str = None, value: int = None) -> Dict[str, Any]:
        """
        提交数据
        @return: 提交结果
        """
        data = self.build(name, value)

        api_data = self._create_api_data(
            url="/api/data",
            method="POST",
            json_data=data
        )

        result = demo_project.data.submit_data(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None
