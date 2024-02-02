# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-13 10:27
# @Author : 毛鹏
import copy
import json
import time
from collections import Counter

import allure

from auto_test.get_project_config import get_project_config
from config.config import PRINT_EXECUTION_RESULTS
from enums.tools_enum import AssEnum, AfterHandleEnum
from models.api_model import TestCaseModel, AssListModel, ApiDataModel
from tools.assertion import Assertion
from tools.data_processor import DataProcessor
from tools.database.mysql_control import MySQLHelper
from tools.decorator.response import log_decorator
from tools.logging_tool.log_control import ERROR


class CaseTool(Assertion):
    data_processor = None

    @log_decorator(PRINT_EXECUTION_RESULTS)
    def case_run(self, func, data: ApiDataModel, data_processor) -> tuple[ApiDataModel, dict]:
        """
        公共请求方法
        @param func: 接口函数
        @param data: ApiDataModel
        @param data_processor: ApiDataModel
        @return: 响应结果
        """
        self.data_processor = data_processor
        res: ApiDataModel = func(data)
        response_dict: dict = res.requests_list[data.step].response.response_json
        return res, response_dict

    def case_ass(self, response_dict: dict, test_case: TestCaseModel, db_is_ass: bool, step: int = None):
        """
        断言处理
        @param response_dict: 响应的字典
        @param test_case: 测试用例数据
        @param db_is_ass: 是否断言
        @param step: 需要断言的步骤
        @return:
        """
        if test_case.case_ass is None:
            ERROR.logger.error(f'用例ID：{test_case.id}的断言未设置，请设置断言后进行测试')
            time.sleep(1)
            return
        if len(test_case.case_ass) == 0:
            assert len(response_dict) > 10
            return
        case_ass = copy.deepcopy(test_case.case_ass)
        if step is not None:
            case_ass = case_ass[step].get(test_case.case_step[step])
        if case_ass is None:
            return
        if isinstance(case_ass, dict):
            allure.attach(str(json.dumps(response_dict, ensure_ascii=False)), '断言-实际值')
            allure.attach(str(json.dumps(case_ass, ensure_ascii=False)), '断言-期望值')
            assert Counter(response_dict) == Counter(case_ass)
        elif isinstance(case_ass, list):
            allure.attach(str(json.dumps(response_dict, ensure_ascii=False)), '断言-实际值')
            ass = []
            for i in case_ass:
                if isinstance(i, AssListModel):
                    ass.append(i.json())
                else:
                    ass.append(i)
            allure.attach(json.dumps(ass), f'断言-期望值')
            for ass_data in case_ass:
                if isinstance(ass_data, dict):
                    ass_data = AssListModel(**ass_data)
                if ass_data.ass_type == AssEnum.response.value:
                    self.response_ass(response_dict, ass_data)
                elif ass_data.ass_type == AssEnum.sql.value:
                    if db_is_ass:
                        self.sql_ass(response_dict, ass_data, test_case.project)
                else:
                    ERROR.logger.error(f'用例ID：{test_case.id}，断言类型错误，请修改断言类型')

    def response_ass(self, response_dict: dict, ass_data: AssListModel):
        """
        响应断言
        @param response_dict: 响应数据
        @param ass_data:
        @return:
        """

        for i in ass_data.expect_list:
            actual = self.data_processor.json_get_path_value(response_dict, i.actual)
            if actual is False:
                # jsonpath未取到值，直接断言错误，请检查表达式
                assert False
            self.ass(response_dict, i.ass_method, actual, i.expect)

    def sql_ass(self, response_dict: dict, ass_data: AssListModel, project):
        """
        sql断言
        @param response_dict:
        @param ass_data:
        @param project: 项目名称
        @return:
        """
        mysql_db_model = get_project_config(project).mysql_db
        mysql_obj: MySQLHelper = MySQLHelper(mysql_db_model)
        query: dict = mysql_obj.execute_query(ass_data.sql)[0]
        if len(query) < 1:
            raise Exception(f'sql语句查询的结果少于1条，请检查sql语句或case本身存在异常\n'
                            f'sql：{ass_data.sql}\n'
                            f'实际查询结果：{query}')
        for i in ass_data.expect_list:
            self.ass(response_dict, i.ass_method, query.get(i.actual), i.expect)

    def ass(self, response_dict: dict, ass_method, actual, expect):
        """
        实际断言语句
        @param response_dict:
        @param ass_method:
        @param actual:
        @param expect:
        @return:
        """
        if expect is not None:
            if '${' in str(expect):
                expect = DataProcessor.remove_parentheses(expect)
                if self.data_processor.json_is_valid_jsonpath(expect):
                    expect = self.data_processor.json_get_path_value(response_dict, expect)
                    if expect is False:
                        # jsonpath未取到值，直接断言错误，请检查表达式
                        assert False
                else:
                    expect = self.data_processor.get_cache(expect)
            getattr(self, ass_method)(actual, expect)
        else:
            getattr(self, ass_method)(actual)

    def after_handle(self, case_after, project):
        """
        用例的后置处理
        @return:
        """
        case_after = [
            {"type": 0, "after_handle": ["DELETE FROM `note_keyword` WHERE `name` = '方法' AND user_id = '100';"]}]
        mysql_db_model = get_project_config(project).mysql_db
        mysql_obj: MySQLHelper = MySQLHelper(mysql_db_model)
        for i in case_after:
            if i.get('type') == AfterHandleEnum.sql.value:
                for sql in i.get('after_handle'):
                    mysql_obj.execute_delete(sql)
