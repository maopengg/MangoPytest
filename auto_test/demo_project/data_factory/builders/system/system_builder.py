# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统构造器 - 对应 /health, /info 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any, Optional

from ..base_builder import BaseBuilder
from auto_test.demo_project.api_manager import demo_project
from ...registry import register_builder


@register_builder("system")
class SystemBuilder(BaseBuilder):
    """
    系统构造器
    对应 /health, /info 接口 (GET)
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token=token, factory=factory)
        # 设置token到API模块
        if token:
            demo_project.system.set_token(token)

    def build(self, **kwargs) -> Dict[str, Any]:
        """
        构造系统信息（不调用API）
        @param kwargs: 构造参数
        @return: 系统信息字典
        """
        return {"type": "system_info"}

    def create(self, **kwargs) -> Optional[Dict[str, Any]]:
        """
        创建系统信息（调用API获取服务器信息）
        @param kwargs: 构造参数
        @return: 服务器信息
        """
        return self.get_server_info()

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        @return: 健康状态
        """
        result = demo_project.system.health_check()
        if result.get("code") == 200:
            return result.get("data")
        return None

    def get_server_info(self) -> Dict[str, Any]:
        """
        获取服务器信息
        @return: 服务器信息
        """
        result = demo_project.system.get_server_info()
        if result.get("code") == 200:
            return result.get("data")
        return None
