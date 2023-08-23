# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from project.aigc.modules.login.login import LoginAPI
from project.aigc.modules.login.model import ResponseModel


@allure.epic("AIGC")
@allure.feature("登录模块")
class TestLogin:

    @allure.story("正确的账号，正确的密码，进行登录")
    @pytest.mark.parametrize("username, password", [("maopeng", "123456")])
    def test_login01(self, username, password):
        result = LoginAPI.api_login(username, password)
        result_dict = ResponseModel.get_obj(result.json())
        assert result_dict.status == 0
        assert result_dict.data.token is not None

    @allure.story("正确的账号，错误的密码，进行登录")
    @pytest.mark.parametrize("username, password", [("maopeng", "1234561")])
    def test_login02(self, username, password):
        result = LoginAPI.api_login(username, password)
        result_dict = ResponseModel.get_obj(result.json())
        assert result_dict.status == 1
        assert result_dict.message == "用户名或密码错误！"

    @allure.story("错误的账号，错误的密码，进行登录")
    @pytest.mark.parametrize("username, password", [("maopeng1", "123456")])
    def test_login03(self, username, password):
        result = LoginAPI.api_login(username, password)
        result_dict = ResponseModel.get_obj(result.json())
        assert result_dict.status == 1
        assert result_dict.message == "用户名或密码错误！"

    @allure.story("登录之后退出登录")
    def test_login04(self):
        result = LoginAPI.api_login_out()
        result_dict = ResponseModel.get_obj(result.json())
        assert result_dict.status == 0