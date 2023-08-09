# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from modules.login.login import Login
from modules.login.model import ResponseModel


@allure.epic("CDXP")
@allure.feature("登录模块")
class TestLogin:

    @allure.story("正确的账号，正确的密码，进行登录")
    @pytest.mark.parametrize("username, password", [("admin", "admin")])
    def test_login01(self, username, password):
        result: ResponseModel = Login.api_login(username, password)
        assert result.status == 0
        assert result.data.access_token is not None

    @allure.story("正确的账号，错误的密码，进行登录")
    @pytest.mark.parametrize("username, password", [("admin", "123456")])
    def test_login02(self, username, password):
        result: ResponseModel = Login.api_login(username, password)
        assert result.status == '1'
        assert result.message == "请输入有效的登录账号或密码"

    @allure.story("错误的账号，错误的密码，进行登录")
    @pytest.mark.parametrize("username, password", [("admin1", "123456")])
    def test_login03(self, username, password):
        result: ResponseModel = Login.api_login(username, password)
        assert result.status == '1'
        assert result.message == "请输入有效的登录账号或密码"
