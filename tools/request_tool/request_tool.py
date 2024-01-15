# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-04 17:23
# @Author : 毛鹏
from urllib.parse import urljoin

import requests
from requests.models import Response

from models.api_model import ApiDataModel, RequestDataModel
from project.get_project_config import get_project_config
from tools.data_processor import DataProcessor
from tools.decorator.case import timer


class RequestTool:
    data_model = None

    @classmethod
    @timer(60)
    def http_request(cls, data_: ApiDataModel) -> ApiDataModel | Response:
        """
        全局请求统一处理
        @param data_: ApiDataModel
        @return: ApiDataModel
        """
        request: RequestDataModel = data_.requests_list[data_.step].request
        return requests.request(method=request.method,
                                url=request.url,
                                headers=request.headers,
                                params=request.params,
                                data=request.data,
                                json=request.json_data,
                                files=request.file
                                )

    @classmethod
    def http(cls, data: ApiDataModel) -> ApiDataModel | Response:
        """
        处理请求的数据，写入到request对象中
        @return:
        """
        group = data.requests_list[data.step]
        group.request.url = urljoin(cls.data_model.host, group.api_data.url)
        group.request.headers = group.api_data.headers if group.api_data.headers else get_project_config(
            data.project).headers
        case_params = data.test_case_data.case_params
        case_data = data.test_case_data.case_data
        case_json = data.test_case_data.case_json
        #
        if data.test_case_data.case_step:
            case_step_name = data.test_case_data.case_step[data.step]
            if case_params:
                case_json = cls.find_value(case_params, case_step_name)
            elif case_data:
                case_json = cls.find_value(case_data, case_step_name)
            elif case_json:
                case_json = cls.find_value(case_json, case_step_name)
        # 解析params
        if case_params is not None:
            path = DataProcessor.replace_text(str(case_params))
            group.request.params = eval(path)
        # 解析 data
        if case_data is not None:
            data_ = DataProcessor.replace_text(str(case_data))
            if type(case_data) == str:
                group.request.data = case_data
            else:
                group.request.data = eval(data_)

        # 解析 data
        if case_json is not None:
            json_data = DataProcessor.replace_text(str(case_json))
            group.request.json_data = eval(json_data)
        return cls.http_request(data)

    @classmethod
    def find_value(cls, case_list, case_step_name):
        for i in case_list:
            for key, value in i.items():
                if key == case_step_name:
                    return value
        return None
