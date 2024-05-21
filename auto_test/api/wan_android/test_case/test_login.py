# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏
import asyncio

import allure
import pytest

from auto_test.api.wan_android.modules_api.login import LoginAPI
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.data_processor import DataProcessor
from tools.decorator.response import case_data


@allure.epic('演示-API自动化-常规API-玩安卓')
@allure.feature('登录模块')
class TestLogin(LoginAPI, CaseTool):
    data_processor: DataProcessor = DataProcessor()

    @pytest.mark.asyncio
    @allure.title('正确的账号，正确的密码，进行登录')
    @allure.description('测试账号登录')
    @case_data(1)
    async def test_01(self, data: ApiDataModel):
        data = await self.api_login(data)
        await asyncio.sleep(5)
        assert data.response.response_dict['data']['nickname'] == "maopeng"

    @pytest.mark.asyncio
    @allure.title('正确的账号，错误的密码，进行登录')
    @allure.description('测试账号登录')
    @case_data(2)
    async def test_02(self, data: ApiDataModel):
        data = await self.api_login(data)
        # assert data.response.response_dict['errorMsg'] == "账号密码不匹配！"
        with allure.step('检查错误消息'):
            expected_error_msg = "账号密码不匹配！"
            actual_error_msg = data.response.response_dict['errorMsg']
            assert actual_error_msg == expected_error_msg
            allure.attach(expected_error_msg, 'Expected Error Message', allure.attachment_type.TEXT)
            allure.attach(actual_error_msg, 'Actual Error Message', allure.attachment_type.TEXT)

    @pytest.mark.asyncio
    @allure.title('错误的账号，错误的密码，进行登录')
    @case_data(3)
    async def test_03(self, data: ApiDataModel):
        data = await self.api_login(data)
        assert data.response.response_dict['errorMsg'] == "账号密码不匹配！"


if __name__ == '__main__':
    pytest.main([r'D:\GitCode\PytestAutoTest\auto_test\api\cdp\test_case\test_login.py::TestLogin'])
