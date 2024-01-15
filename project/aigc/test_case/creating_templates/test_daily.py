# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 16:02
# @Author : 毛鹏
import allure

from models.api_model import ApiDataModel
from project.aigc.modules.creating_templates.daily import CreatingTemplatesAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic('AIGC')
@allure.feature('5、日报生成')
class TestDaily(CreatingTemplatesAPI, CaseTool):

    @allure.story('1、生成前数据校验')
    @allure.title('1、数据校验-无数据')
    @case_data(70)
    def test_api_xhs_check1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_check, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、生成前数据校验')
    @allure.title('2、数据校验-有数据')
    @case_data(71)
    def test_api_xhs_check2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_check, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、生成前数据校验')
    @allure.title('3、数据校验-有未映射数据')
    @case_data(72)
    def test_api_xhs_check3(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_check, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('2、查询日报')
    @allure.title('1、查询日报-无数据')
    @case_data(79)
    def test_api_xhs_get1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_get, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('2、查询日报')
    @allure.title('1、查询日报-有数据')
    @case_data(80)
    def test_api_xhs_get2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_get, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('3、生成日报')
    @allure.title('1、生成日报')
    @case_data(81)
    def test_api_ai_generateDaily1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_ai_generateDaily, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
