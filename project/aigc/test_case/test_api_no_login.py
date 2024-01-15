# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure

from models.api_model import ApiDataModel
from project.aigc.modules.api_no_login import NoLoginAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic("AIGC")
@allure.feature("0、未登录")
@allure.story('1、未登录')
class TestNoLogin(NoLoginAPI, CaseTool):

    @allure.title('1.未登录调用-小红书每日报告list')
    @case_data(83)
    def test_no_login1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login1, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('2.未登录调用-查询关键词（根据分类ID）')
    @case_data(84)
    def test_no_login2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login2, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('3.未登录调用-生成小红书标题')
    @case_data(85)
    def test_no_login3(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login3, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('4.未登录调用-生成小红书内容')
    @case_data(86)
    def test_no_login4(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login4, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('5.未登录调用-查询账户是否存在')
    @case_data(87)
    def test_no_login5(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login5, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('6.未登录调用-查询账户列表')
    @case_data(88)
    def test_no_login6(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login6, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('7.未登录调用-初始化账户信息')
    @case_data(89)
    def test_no_login7(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login7, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('8.未登录调用-校验品牌名称 OR 账户')
    @case_data(90)
    def test_no_login8(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login8, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('9.未登录调用-添加品牌')
    @case_data(91)
    def test_no_login9(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login9, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('10.未登录调用-查询品牌列表')
    @case_data(92)
    def test_no_login10(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login10, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('11.未登录调用-修改品牌')
    @case_data(93)
    def test_no_login11(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login11, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('12.未登录调用-根据品牌ID 删除品牌')
    @case_data(94)
    def test_no_login12(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login12, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('13.未登录调用-同步当天数据')
    @case_data(95)
    def test_no_login13(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login13, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('14.未登录调用-同步指定日期数据')
    @case_data(96)
    def test_no_login14(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login14, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('15.未登录调用-同步数据（根据品牌和日期）')
    @case_data(97)
    def test_no_login15(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login15, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('16.未登录调用-获取最近同步记录')
    @case_data(98)
    def test_no_login16(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login16, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('17.未登录调用-单元数据列表')
    @case_data(99)
    def test_no_login17(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login17, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('18.未登录调用-修改单元数据')
    @case_data(100)
    def test_no_login18(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login18, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('19.未登录调用-单元上传Excel数据')
    @case_data(101)
    def test_no_login19(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login19, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('20.未登录调用-关键词列表')
    @case_data(102)
    def test_no_login20(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login20, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('21.未登录调用-修改关键词')
    @case_data(103)
    def test_no_login21(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login21, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('22.未登录调用-关键词上传Excel数据')
    @case_data(104)
    def test_no_login22(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login22, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('23.未登录调用-获取笔记筛选下拉选项')
    @case_data(105)
    def test_no_login23(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login23, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('24.未登录调用-查询笔记列表')
    @case_data(106)
    def test_no_login24(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login24, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('25.未登录调用-根据主键Id 获取笔记信息')
    @case_data(107)
    def test_no_login25(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login25, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('26.未登录调用-笔记-添加关键词')
    @case_data(108)
    def test_no_login26(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login26, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('27.未登录调用-查询分类')
    @case_data(109)
    def test_no_login27(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login27, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('28.未登录调用-校验是否需要处理单元关键词数据')
    @case_data(110)
    def test_no_login28(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login28, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('29.未登录调用-查询单元，搜索总数量')
    @case_data(111)
    def test_no_login29(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login29, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('30.未登录调用-下载导入模板')
    @case_data(112)
    def test_no_login30(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login30, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('31.未登录调用-生成日报')
    @case_data(113)
    def test_no_login31(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login31, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('32.未登录调用-查询日报列表')
    @case_data(114)
    def test_no_login32(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login32, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('33.未登录调用-查询日报')
    @case_data(115)
    def test_no_login33(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login33, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('34.未登录调用-保存日报')
    @case_data(116)
    def test_no_login34(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login34, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('35.未登录调用-修改日报')
    @case_data(117)
    def test_no_login35(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login35, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.title('36.未登录调用-终止生成小红书笔记')
    @case_data(118)
    def test_no_login36(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.no_login36, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
