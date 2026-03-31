# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder基类
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod
import hashlib

from auto_test.demo_project.api_manager import demo_project
from models.api_model import ApiDataModel, RequestModel


class BaseBuilder(ABC):
    """
    数据构造器基类
    所有具体构造器都需要继承此类
    """

    def __init__(self, token: str = None, factory=None):
        self.token = token
        self.factory = factory  # 关联的数据工厂实例
        self._data: Dict[str, Any] = {}  # 构造的数据
        self._created_items: List[Dict] = []  # 已创建的条目

    def set_token(self, token: str):
        """设置token"""
        self.token = token
        return self

    def set_factory(self, factory):
        """设置数据工厂"""
        self.factory = factory
        return self

    def _create_api_data(self, url: str, method: str = "GET", json_data: Dict = None,
                        params: Dict = None, headers: Dict = None,
                        file_data: List[Tuple] = None) -> ApiDataModel:
        """
        创建ApiDataModel对象
        @param url: 请求URL
        @param method: 请求方法
        @param json_data: JSON数据
        @param params: URL参数
        @param headers: 请求头
        @param file_data: 文件数据 [(field_name, (filename, file_object)), ...]
        @return: ApiDataModel
        """
        request_headers = headers or {}
        if self.token:
            request_headers["X-Token"] = self.token

        request_model = RequestModel(
            url=url,
            method=method,
            headers=request_headers,
            json=json_data,
            params=params,
            file=file_data
        )
        return ApiDataModel(request=request_model)

    @abstractmethod
    def build(self, **kwargs) -> Dict[str, Any]:
        """
        构造数据
        @param kwargs: 构造参数
        @return: 构造的数据
        """
        pass

    def _register_created(self, item: Dict):
        """注册已创建的条目"""
        self._created_items.append(item)
        if self.factory:
            # 同时注册到工厂
            data_type = self.__class__.__name__.lower().replace('builder', '')
            self.factory.register_created(data_type, item)

    def get_created(self) -> List[Dict]:
        """获取已创建的条目"""
        return self._created_items.copy()

    def clear_created(self):
        """清空已创建记录"""
        self._created_items.clear()

    def _generate_password(self, password: str = "123456") -> str:
        """生成MD5密码"""
        return hashlib.md5(password.encode()).hexdigest()

    def cleanup(self):
        """清理所有创建的数据"""
        for item in self._created_items[:]:
            try:
                item_id = item.get('id')
                if item_id and hasattr(self, 'delete'):
                    self.delete(item_id)
            except Exception:
                pass
        self._created_items.clear()
