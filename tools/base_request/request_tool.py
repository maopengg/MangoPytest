# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-04 17:23
# @Author : 毛鹏

from urllib.parse import urljoin

import requests
from requests.models import Response

from models.api_model import ApiDataModel, RequestModel, ResponseModel
from settings.settings import PROXY
from tools.data_processor import DataProcessor
from tools.decorator.response import timer


class RequestTool:
    data_processor: DataProcessor = DataProcessor()

    def http(self, data: ApiDataModel) -> ApiDataModel | Response:
        """
        处理请求的数据，写入到request对象中
        @return:
        """
        data.request.url = urljoin(data.base_data.host, data.request.url)
        for key, value in data.request:
            if value is not None and key != 'file':
                value = self.data_processor.replace(value)
                if key == 'headers' and isinstance(value, str):
                    value = self.data_processor.replace(self.data_processor.loads(value))
                setattr(data.request, key, value)
            elif key == 'file':
                if data.request.file:
                    file = []
                    for i in data.request.file:
                        i: dict = i
                        for k, v in i.items():
                            file_name = self.data_processor.identify_parentheses(v)[0].replace('(', '').replace(')', '')
                            path = self.data_processor.replace(v)
                            file.append((k, (file_name, open(path, 'rb'))))
                    data.request.file = file
        data.response = self.http_request(data.request)[0]
        return data

    @timer
    def http_request(self, request_model: RequestModel) -> Response | ResponseModel:
        """
        全局请求统一处理
        @param request_model: RequestDataModel
        @return: ApiDataModel
        """
        return requests.request(
            method=request_model.method,
            url=request_model.url,
            headers=request_model.headers,
            params=request_model.params,
            data=request_model.data,
            json=request_model.json_data,
            files=request_model.file,
            proxies=PROXY
        )
