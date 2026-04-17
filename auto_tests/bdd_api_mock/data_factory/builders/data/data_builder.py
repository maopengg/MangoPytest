# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据构造器 - 对应 /api/data 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from typing import Dict, Any

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock
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
        self._created = []

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

        bdd_api_mock.data.set_token(self.token)
        result = bdd_api_mock.data.submit_data(**data)
        if result.get("code") == 200:
            created_data = result.get("data")
            if created_data:
                self._created.append(created_data)
            return created_data
        return None

    def create(self, name: str = None, value: int = None) -> Dict[str, Any]:
        """
        创建数据（别名：submit）
        @return: 创建的数据
        """
        return self.submit(name, value)

    def create_submitted(self, name: str = None, value: int = None) -> Dict[str, Any]:
        """
        创建已提交的数据
        @return: 已提交的数据
        """
        return self.submit(name, value)

    def create_batch(self, count: int = 5) -> list:
        """
        批量创建数据
        @param count: 数量
        @return: 创建的数据列表
        """
        results = []
        for i in range(count):
            data = self.submit(name=f"batch_data_{i}", value=100 + i)
            if data:
                results.append(data)
        return results

    def cleanup(self):
        """
        清理创建的数据
        """
        # 这里可以实现清理逻辑
        self._created.clear()
