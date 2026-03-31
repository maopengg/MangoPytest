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
        super().__init__(token, factory)

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        @return: 健康状态
        """
        api_data = self._create_api_data(
            url="/health",
            method="GET"
        )

        result = demo_project.system.health_check(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None

    def get_server_info(self) -> Dict[str, Any]:
        """
        获取服务器信息
        @return: 服务器信息
        """
        api_data = self._create_api_data(
            url="/info",
            method="GET"
        )

        result = demo_project.system.get_server_info(api_data)
        if result.response and result.response.json().get("code") == 200:
            return result.response.json()["data"]
        return None
