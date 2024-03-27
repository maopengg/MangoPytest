# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-04 17:23
# @Author : 毛鹏

from urllib.parse import urljoin

import requests
from requests.models import Response

from models.api_model import ApiDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import timer

proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'https://127.0.0.1:7890'
}
class RequestTool:
    data_processor: DataProcessor = DataProcessor()

    def http(self, data: ApiDataModel) -> ApiDataModel | Response:
        """
        处理请求的数据，写入到request对象中
        @return:
        """
        return self.http_request(self.request_data(data))

    @timer
    def http_request(self, data: ApiDataModel) -> Response:
        """
        全局请求统一处理
        @param data: RequestDataModel
        @return: ApiDataModel
        """
        return requests.request(
            method=data.request.method,
            url=urljoin(data.base_data.host, data.request.url),
            headers=data.request.headers,
            params=data.request.params,
            data=data.request.data,
            json=data.request.json_data,
            files=data.request.file,
            proxies=proxies
        )

    def request_data(self, data: ApiDataModel) -> ApiDataModel:
        """
        检查请求信息中是否存在变量进行替换
        @param data:RequestModel
        @return:
        """
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
        return data
