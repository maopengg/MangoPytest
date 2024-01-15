# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-18 14:37
# @Author : 毛鹏

import allure

from models.api_model import ApiDataModel
from project.aigc.modules.xhs_notes.note_taking import NoteTakingAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic("AIGC")
@allure.feature("小红书")
@allure.story('3、小红书笔记记录')
class TestNoteTaking(NoteTakingAPI, CaseTool):

    @allure.title('1、获取笔记筛选下拉选项')
    @case_data(39)
    def test_note_taking01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_note_filter_dropdown_options, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('2、查询笔记列表')
    @case_data(40)
    def test_note_taking02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_query_note_list, data)
        # 设置缓存给下个case使用
        self.set_cache('40_response_dict', response_dict)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('3、带条件的查询笔记列表')
    @case_data(41)
    def test_note_taking03(self, data: ApiDataModel):
        # 取出上一步的响应结果并设置到缓存
        previous_step_response_dict: dict = self.get_cache('40_response_dict')
        second_type = self.json_get_path_value(previous_step_response_dict, '$.data.records[0].secondType')
        theme_direction = self.json_get_path_value(previous_step_response_dict, '$.data.records[0].themeDirection')
        title = self.json_get_path_value(previous_step_response_dict, '$.data.records[0].title')
        self.set_cache('talentType', second_type)
        self.set_cache('themeDirection', theme_direction)
        self.set_cache('keywords', title)
        data, response_dict = self.case_run(self.api_query_note_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('4、根据主键Id 获取笔记信息')
    @case_data(42)
    def test_note_taking04(self, data: ApiDataModel):
        # 取出上一步的响应结果并设置到缓存
        previous_step_response_dict: dict = self.get_cache('40_response_dict')
        _id = self.json_get_path_value(previous_step_response_dict, '$.data.records[0].id')
        self.set_cache('test_note_taking04_id', str(_id))

        data, response_dict = self.case_run(self.api_query_note_key, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

