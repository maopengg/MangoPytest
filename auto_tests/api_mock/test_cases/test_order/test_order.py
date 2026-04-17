# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 14:05
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mock.abstract.order.order import OrderAPI
from core.models.api_model import ApiDataModel
from core.api.case_tool import CaseTool
from core.decorators.api import case_data
from core.utils.obtain_test_data  import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
class TestOrder(OrderAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([38, 39, 40, 41])
    def test_01(self, data: ApiDataModel):
        data = self.create_order(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([42, 43, 44, 45])
    def test_02(self, data: ApiDataModel):
        if data.test_case.id in [42, 43]:
            # 获取所有订单
            data = self.get_all_orders(data)
        elif data.test_case.id in [44, 45]:
            # 根据ID获取订单
            data = self.get_order_by_id(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([46, 47, 48])
    def test_03(self, data: ApiDataModel):
        data = self.update_order_info(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([49, 50, 51])
    def test_04(self, data: ApiDataModel):
        data = self.delete_order(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main(['-v', 'test_order.py'])
