# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure

from config.get_path import ensure_path_sep
from models.api_model import ApiDataModel
from project.aigc.modules.creating_templates.data_mapping import DataMappingAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic("AIGC")
@allure.feature("4、1、单元数据映射")
class TestUnitDataMapping(DataMappingAPI, CaseTool):

    @allure.story('1、单元数据列表')
    @allure.title('1、列表默认加载')
    @case_data(31)
    def test_unit_list01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、单元数据列表')
    @allure.title('1、搜索品牌')
    @case_data(32)
    def test_unit_list02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、单元数据列表')
    @allure.title('2、组合搜索')
    @case_data(33)
    def test_unit_list03(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、单元数据列表')
    @allure.title('3、搜索单元')
    @case_data(34)
    def test_unit_list04(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、单元数据列表')
    @allure.title('4、搜索KOL')
    @case_data(35)
    def test_unit_list05(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、单元数据列表')
    @allure.title('5、搜索投放形式')
    @case_data(36)
    def test_unit_list06(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、单元数据列表')
    @allure.title('6、搜索状态')
    @case_data(37)
    def test_unit_list07(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('2、修改单元数据')
    @allure.title('1、修改单元数据')
    @case_data(38)
    def test_unit_update01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_update, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('3、数据映射')
    @allure.title('1、查询单元，搜索总数量')
    @case_data(73)
    def test_xhs_count(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_count, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、下载模板')
    @allure.title('1、信息流下载-待处理')
    @case_data(74)
    def test_xhs_download1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_download, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、下载模板')
    @allure.title('2、信息流下载-指定品牌')
    @case_data(75)
    def test_xhs_download2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_download, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、下载模板')
    @allure.title('3、信息流下载-指定品牌，广告单元')
    @case_data(76)
    def test_xhs_download3(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_xhs_download, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
        if data.db_is_ass:
            sql = "select COUNT(1) as counts from unit_data where account_id in (select DISTINCT account_id from brands where account_name='柳丝木' and user_id=121) and unit_name LIKE '%哈密瓜%' and `status`=0"
            query_counts: int = self.data_model.mysql_obj.execute_query(sql)[0]['counts']
            file_path = ensure_path_sep('/case_files/down_tmp/' + 'tmp.xlsx')
            assert self.excel_rows(file_path) - 2 == query_counts

    @allure.story('5、上传信息流文件')
    @allure.title('1、上传信息流文件')
    @case_data(50)
    def test_unit_upload01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_upload, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('5、上传信息流文件')
    @allure.title('2、上传错误信息流文件')
    @case_data(53)
    def test_unit_upload02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_unit_upload2, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
