# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure

from models.api_model import ApiDataModel
from project.aigc.modules.creating_templates.data_mapping import DataMappingAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool

@allure.epic("AIGC")
@allure.feature("4、2、关键字数据映射")
class TestDataKeyWordMapping(DataMappingAPI, CaseTool):
    @allure.story('1、关键字数据列表')
    @allure.title('1、列表默认加载')
    @case_data(43)
    def test_key_word_list01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、关键字数据列表')
    @allure.title('2、搜索品牌')
    @case_data(44)
    def test_key_word_list02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、关键字数据列表')
    @allure.title('3、组合搜索')
    @case_data(45)
    def test_key_word_list03(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、关键字数据列表')
    @allure.title('4、搜索词包')
    @case_data(46)
    def test_key_word_list04(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、关键字数据列表')
    @allure.title('5、搜索KOL')
    @case_data(47)
    def test_key_word_list05(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、关键字数据列表')
    @allure.title('6、搜索状态')
    @case_data(48)
    def test_key_word_list06(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('2、修改关键词数据')
    @allure.title('1、修改关键词数据')
    @case_data(49)
    def test_key_word_update01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_update, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('3、上传关键字文件')
    @allure.title('1、上传关键字文件')
    @case_data(51)
    def test_key_word_upload01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_upload, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('3、上传关键字文件')
    @allure.title('2、上传错误关键词文件')
    @case_data(54)
    def test_key_word_upload02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_key_word_upload2, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、下载模板')
    @allure.title('1、关键词下载-待处理')
    @case_data(77)
    def test_xhs_download4(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_download, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、下载模板')
    @allure.title('2、关键词下载-指定品牌')
    @case_data(78)
    def test_xhs_download5(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_download, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
