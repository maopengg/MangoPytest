# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-09-04 17:23
# @Author : 毛鹏

from urllib.parse import urljoin

from mangokit import requests, DataProcessor
from requests.models import Response

from models.api_model import ApiDataModel, RequestModel, ResponseModel
from tools.decorator.response import timer, log_decorator
from tools.log import log


class RequestTool:
    data_processor: DataProcessor = None

    @log_decorator
    def http(self, data: ApiDataModel, is_replace=True) -> ApiDataModel | Response:
        """
        处理请求的数据，写入到request对象中
        :param data: ApiDataModel
        :param is_replace: 是否过滤请求中的${}, 如果数据本身就有${}，那需要传false
        :return:
        """
        data.request.url = urljoin(data.base_data.host, data.request.url)
        if is_replace:
            for key, value in data.request:
                if value is not None and key != 'file':
                    if is_replace:
                        value = self.data_processor.replace(value)
                        setattr(data.request, key, value)
                elif key == 'file':
                    if data.request.file:
                        file = []
                        for i in data.request.file:
                            i: dict = i
                            for k, v in i.items():
                                file_name = self.data_processor \
                                    .identify_parentheses(v)[0] \
                                    .replace('(', '') \
                                    .replace(')', '')
                                if is_replace:
                                    path = self.data_processor.replace(v)
                                    file.append((k, (file_name, open(path, 'rb'))))
                        data.request.file = file
        data.response = self.http_request(data.request)
        return data

    @timer
    def http_request(self, request_model: RequestModel) -> ResponseModel | Response:
        """
        全局请求统一处理
        @param request_model: RequestDataModel
        @return: ApiDataModel
        """
        log.debug(f'请求前置：{request_model.model_dump_json()}')
        return requests.request(
            method=request_model.method,
            url=request_model.url,
            headers=request_model.headers,
            params=request_model.params,
            data=request_model.data,
            json=request_model.json_data,
            files=request_model.file,
        )


if __name__ == '__main__':
    requests1 = RequestTool()
    response :ResponseModel = requests1.http_request(RequestModel(
        **{}))
    print(response.response_text)
