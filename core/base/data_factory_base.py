# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据工厂基类
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar

T = TypeVar('T')


class DataFactoryBase(ABC):
    """
    数据工厂基类
    提供数据创建、管理和清理的基础功能
    """

    def __init__(self):
        self.created_data: Dict[str, List[Dict]] = {}
        self.token: Optional[str] = None
        self._context: Dict[str, Any] = {}  # 上下文数据，用于模块间数据传递

    def set_context(self, key: str, value: Any):
        """设置上下文数据"""
        self._context[key] = value

    def get_context(self, key: str, default=None) -> Any:
        """获取上下文数据"""
        return self._context.get(key, default)

    def clear_context(self):
        """清空上下文"""
        self._context.clear()

    def register_created(self, data_type: str, data: Dict):
        """注册已创建的数据"""
        if data_type not in self.created_data:
            self.created_data[data_type] = []
        self.created_data[data_type].append(data)

    def get_created(self, data_type: str) -> List[Dict]:
        """获取已创建的数据"""
        return self.created_data.get(data_type, [])

    @abstractmethod
    def cleanup_all(self):
        """清理所有创建的数据"""
        pass

    def generate_uuid(self, length: int = 8) -> str:
        """生成UUID"""
        return uuid.uuid4().hex[:length]
