# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-09-04 17:23
# @Author : 毛鹏
import os
from typing import Optional
from urllib.parse import urljoin

from mangokit.apidrive import requests
from requests.models import Response

from models.api_model import ApiDataModel, RequestModel, ResponseModel
from tools.decorator.response import timer, log_decorator
from tools.log import log
from tools.obtain_test_data import ObtainTestData


class RequestTool:
    test_data: Optional[ObtainTestData | None] = None

    @log_decorator
    def http(self, data: ApiDataModel, is_replace=True) -> ApiDataModel | Response:
        """
        处理请求的数据，写入到request对象中
        :param data: ApiDataModel
        :param is_replace: 是否过滤请求中的${{}}, 如果数据本身就有${{}}，那需要传false
        :return:
        """
        log.debug(f'清洗请求数据之前，请求数据：{data.request.model_dump_json()}')
        log.debug(f'清洗请求数据之前，缓存数据：{self.test_data.get_all()}')
        data.request.url = urljoin(data.base_data.host, data.request.url)
        if is_replace:
            for key, value in data.request:
                if value is not None and key != 'file':
                    if is_replace:
                        value = self.test_data.replace(value)
                        setattr(data.request, key, value)
                elif key == 'file':
                    if data.request.file:
                        file = []
                        for i in data.request.file:
                            for k, v in i.items():
                                if 'get_file' not in v:
                                    v = self.test_data.replace(v)
                                if os.path.isabs(v):
                                    log.debug(f'文件路径为绝对路径，直接使用')
                                    file_path = v
                                else:
                                    file_path = self.test_data.get_file(data.base_data.project.get('name'), v)
                                file_name = os.path.basename(file_path)
                                file.append((k, (file_name, open(file_path, 'rb'))))
                        data.request.file = file
        log.debug(f'清洗请求数据之后，请求数据：{data.request.model_dump()}')
        data.response = self.http_request(data.request)
        return data

    @timer
    def http_request(self, request_model: RequestModel) -> ResponseModel | Response:
        """
        带装饰器，进行内部数据格式化的请求
        @param request_model: RequestDataModel
        @return: ApiDataModel
        """
        return self.custom_http(request_model)

    @staticmethod
    def custom_http(request_model: RequestModel) -> Response:
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
        )
