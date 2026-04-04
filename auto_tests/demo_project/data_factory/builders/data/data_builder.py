# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据构造器 - 对应 /api/data 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from typing import Dict, Any

from auto_tests.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("data")
class DataBuilder:
    """
    数据构造器
    对应 /api/data 接口 (POST)
    """

    def __init__(self, token: str = None, factory=None):
        self.token = token
        self.factory = factory

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

        demo_project.data.set_token(self.token)
        result = demo_project.data.submit_data(**data)
        if result.get("code") == 200:
            return result.get("data")
        return None
