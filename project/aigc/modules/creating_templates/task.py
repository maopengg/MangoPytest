# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import copy
import time
from datetime import datetime, timedelta

from models.api_model import ApiDataModel
from models.models import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.mysql_tool.mysql_control import MySQLHelper
from tools.request_tool.request_tool import RequestTool


class TaskAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(16)
    def api_task_get(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'

        # 下面要修改
        yesterday_str = cls.get_before_time()
        if data.db_is_ass:
            sql = f'delete from info_flow_table where date="{yesterday_str}";'
            cls.data_model.mysql_obj.execute_update(sql)
        response = cls.http(data)
        return response

    @classmethod
    @around(17)
    def api_task_get_by_day(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'
        run_date = data.test_case_data.case_data.get("date")
        data.test_case_data.case_data = run_date
        # 下面要修改
        if data.db_is_ass:
            sql = f'delete from info_flow_table where date="{run_date}";'
            cls.data_model.mysql_obj.execute_update(sql)
        header = copy.deepcopy(cls.data_model.headers)
        header["Content-Type"] = 'text/plain'
        response = cls.http(data)
        return response

    @classmethod
    @around(18)
    def api_manage_sync(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'

        # 下面要修改
        yesterday_str = cls.get_before_time()
        if data.db_is_ass:
            sql = f'delete from info_flow_table where date="{yesterday_str}";'
            cls.data_model.mysql_obj.execute_update(sql)
        data.test_case_data.case_params["date"] = yesterday_str
        response = cls.http(data)
        return response

    @classmethod
    @around(18)
    def api_manage_sync2(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'

        # 下面要修改
        yesterday_str = cls.get_before_time()
        data.test_case_data.case_params["date"] = yesterday_str
        response1 = cls.http(data)
        response = cls.http(data)
        return response

    @classmethod
    @around(19)
    def api_manage_sync_last(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'

        # 下面要修改
        response = cls.http(data)
        return response


if __name__ == '__main__':
    pass
