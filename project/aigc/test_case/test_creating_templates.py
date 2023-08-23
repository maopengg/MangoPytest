# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure

from project.aigc.modules.creating_templates.creating_templates import CreatingTemplatesAPI
from project.aigc.modules.creating_templates.model import ResponseModel


@allure.epic("AIGC")
@allure.feature("创作模板")
class TestCreatingTemplates:

    @allure.story("日报-小红书日报-列表接口")
    def test_creating_templates_list(self):
        response = CreatingTemplatesAPI.api_daily_list()
        result = ResponseModel(**response.json())
        assert result.status == 0
