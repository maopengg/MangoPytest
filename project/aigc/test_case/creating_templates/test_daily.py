# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure

from models.api_model import TestCaseModel
from project.aigc.modules.creating_templates.daily import CreatingTemplatesAPI
from project.aigc.modules.creating_templates.model import ResponseModel
from tools.decorator.response import testdata


@allure.epic('AIGC')
@allure.feature('创作模板')
@allure.story('小红书笔记')
class TestDaily:

    @testdata(6)
    def test_daily_list(self, test_data: TestCaseModel):
        with allure.title(test_data.name):
            response = CreatingTemplatesAPI.api_daily_list()
            result = ResponseModel(**response.json())
            assert result.status == 0
