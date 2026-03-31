# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景基类
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, List
from abc import ABC, abstractmethod


class BaseScenario(ABC):
    """
    预组装场景基类
    用于封装复杂的测试数据准备场景
    """

    def __init__(self, factory):
        self.factory = factory
        self.token = factory.token if factory else None
        self._created_data: Dict[str, List[Dict]] = {}

    @abstractmethod
    def setup(self, **kwargs) -> Dict[str, Any]:
        """
        设置场景数据
        @param kwargs: 场景参数
        @return: 场景数据
        """
        pass

    @abstractmethod
    def teardown(self):
        """
        清理场景数据
        """
        pass

    def _record(self, data_type: str, data: Dict):
        """记录创建的数据"""
        if data_type not in self._created_data:
            self._created_data[data_type] = []
        self._created_data[data_type].append(data)

    def get_created(self, data_type: str = None) -> Dict[str, List[Dict]] or List[Dict]:
        """
        获取创建的数据
        @param data_type: 数据类型，不传则返回所有
        @return: 创建的数据
        """
        if data_type:
            return self._created_data.get(data_type, [])
        return self._created_data

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动清理"""
        self.teardown()
        return False
