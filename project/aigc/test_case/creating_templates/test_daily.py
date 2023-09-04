# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure

from project.aigc.modules.creating_templates.daily import CreatingTemplatesAPI
from project.aigc.modules.creating_templates.model import ResponseModel


@allure.epic('AIGC')
@allure.feature('创作模板')
@allure.story('小红书笔记')
class TestDaily:

    @allure.title('日报-小红书日报-列表接口')
    def test_daily_list(self):
        response = CreatingTemplatesAPI.api_daily_list()
        result = ResponseModel(**response.json())
        assert result.status == 0
