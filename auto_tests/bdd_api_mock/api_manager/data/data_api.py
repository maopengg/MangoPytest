# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据API - 使用 Core APIClient
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from ..base import DemoProjectBaseAPI


class DataAPI(DemoProjectBaseAPI):
    """数据API - 对应 /api/data 接口"""

    def submit_data(self, name: str, value: int) -> dict:
        """
        提交数据接口
        POST /api/data
        @param name: 数据名称
        @param value: 数据值
        @return: 响应字典
        """
        response = self.client.post("/api/data", json={"name": name, "value": value})
        return response.data
