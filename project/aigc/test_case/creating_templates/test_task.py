# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏
import allure
import time
from models.api_model import ApiDataModel
from project.aigc.modules.creating_templates.task import TaskAPI
from tools.decorator.response import case_data
from tools.mysql_tool.mysql_control import MySQLHelper
from tools.request_tool.case_tool import CaseTool


@allure.epic("AIGC")
@allure.feature("2、定时调度")
class TestTask(TaskAPI, CaseTool):

    @allure.story('1、同步数据')
    @allure.title('1、同步当天数据')
    @case_data(26)
    def test_task_get01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_task_get, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
        if data.db_is_ass:
            sql_after = f'select COUNT(1) as counts from info_flow_table where date="{self.get_before_time()}";'
            query: dict = self.data_model.mysql_obj.execute_query(sql_after)[0]
            assert query["counts"] > 0

    @allure.story('1、同步数据')
    @allure.title('2、同步指定日期数据')
    @case_data(27)
    def test_task_get_by_day01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_task_get_by_day, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
        if data.db_is_ass:
            run_date = data.test_case_data.case_data
            sql_after = f'select COUNT(1) as counts from info_flow_table where date="{run_date}";'
            query: dict = self.data_model.mysql_obj.execute_query(sql_after)[0]
            assert query["counts"] > 0

    @allure.story('1、同步数据')
    @allure.title('3、同步数据(根据品牌和日期)')
    @case_data(28)
    def test_manage_sync01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_manage_sync, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)
        if data.db_is_ass:
            sqlsync = f'select `status` from sync_log ORDER BY create_time DESC LIMIT 1;'
            status: bool = True
            loops: int = 0
            while (status):
                p = MySQLHelper(self.data_model.mysql_db)
                querysync: dict = p.execute_query(sqlsync)[0]
                if querysync["status"] == 1:
                    break
                if loops > 30:
                    assert 1 == 2
                loops += 1
                time.sleep(5)
            sql_after = f'select COUNT(1) as counts from info_flow_table where date="{self.get_before_time()}";'
            query: dict = self.data_model.mysql_obj.execute_query(sql_after)[0]
            assert query["counts"] > 0

    @allure.story('1、同步数据')
    @allure.title('4、正在同步中')
    @case_data(30)
    def test_manage_sync02(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_manage_sync2, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)

    @allure.story('2、获取最近同步记录')
    @allure.title('1、获取最近同步记录')
    @case_data(29)
    def test_manage_sync_last01(self, data: ApiDataModel):
        data, response_dict = self.case_run(self.api_manage_sync_last, data)
        self.case_ass(response_dict, data.test_case_data, data.db_is_ass)