# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据管理API - 不依赖Excel装饰器
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from typing import Dict, Any, Optional

from core.api.client import APIClient


class DataAPI:
    """数据管理API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def submit_data(self, name: str, value: str, type: str, 
                    description: Optional[str] = None) -> Dict[str, Any]:
        """
        提交数据接口
        @param name: 数据名称
        @param value: 数据值
        @param type: 数据类型
        @param description: 数据描述
        @return: 响应数据字典
        """
        data = {
            "name": name,
            "value": value,
            "type": type
        }
        if description:
            data["description"] = description
        
        response = self.client.post("/api/data", json=data)
        return response.data
