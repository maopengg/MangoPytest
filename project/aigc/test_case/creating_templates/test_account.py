# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-09-13 16:02
# @Author : 吴强
import allure

from models.api_model import ApiDataModel
from project.aigc.modules.creating_templates.account import AccountAPI
from tools.decorator.response import case_data
from tools.request_tool.case_tool import CaseTool


@allure.epic('AIGC')
@allure.feature('3、品牌管理')
class TestAccount(AccountAPI, CaseTool):

    @allure.story('1、新增品牌前校验')
    @allure.title('1、正确的账户名称和ID')
    @case_data(11)
    def test_account_check1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_account_exists, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、新增品牌前校验')
    @allure.title('2、错误的账户名称')
    @case_data(12)
    def test_account_check2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_account_exists, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、新增品牌前校验')
    @allure.title('3、错误的账户ID')
    @case_data(13)
    def test_account_check3(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_account_exists, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、新增品牌前校验')
    @allure.title('4、不输入账户名称')
    @case_data(14)
    def test_account_check4(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_account_exists, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('1、新增品牌前校验')
    @allure.title('5、不输入账户ID')
    @case_data(15)
    def test_account_check5(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_account_exists, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('2、查询账户列表')
    @allure.title('1、查询账户列表')
    @case_data(16)
    def test_account_list1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_account_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('3、初始化账户信息')
    @allure.title('1、初始化账户信息')
    @case_data(17)
    def test_account_init_account1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_account_init_account, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、校验品牌名称OR账户')
    @allure.title('1、品牌名称不重复')
    @case_data(18)
    def test_api_brands_check1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_check, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、校验品牌名称OR账户')
    @allure.title('2、品牌名称重复')
    @case_data(19)
    def test_api_brands_check2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_check, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('4、校验品牌名称OR账户')
    @allure.title('3、品牌ID重复')
    @case_data(20)
    def test_api_brands_check3(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_check, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('5、添加品牌')
    @allure.title('1、添加品牌')
    @case_data(21)
    def test_api_brands_add1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_add, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('6、修改品牌')
    @allure.title('1、修改品牌')
    @case_data(25)
    def test_api_brands_update1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_update, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('6、修改品牌')
    @allure.title('2、修改品牌KIP')
    @case_data(69)
    def test_api_brands_update2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_update2, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('7、查询品牌列表')
    @allure.title('1、查询品牌列表')
    @case_data(22)
    def test_api_brands_list1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_list, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('8、删除品牌')
    @allure.title('1、删除品牌-品牌不存在')
    @case_data(23)
    def test_api_brands_delete1(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_delete, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('8、删除品牌')
    @allure.title('2、删除品牌-品牌存在')
    @case_data(24)
    def test_api_brands_delete2(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_brands_delete, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
