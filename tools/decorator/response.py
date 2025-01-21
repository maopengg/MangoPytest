# -*- coding: utf-8 -*-
# @Description:
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import functools
import json
import time

import allure
import pytest
from requests.models import Response

from enums.api_enum import MethodEnum
from exceptions import PytestAutoTestError
from exceptions.error_msg import ERROR_MSG_0350
from models.api_model import ApiDataModel, ResponseModel, ApiTestCaseModel, RequestModel, ApiInfoModel
from settings.settings import PRINT_EXECUTION_RESULTS, REQUEST_TIMEOUT_FAILURE_TIME
from sources import SourcesData
from tools.log import log


def case_data(case_id: int | list[int] | None = None, case_name: str | list[str] | None = None):
    def decorator(func):
        log.debug(f'开始查询用例，用例ID:{case_id} 用例名称：{case_name}')
        if case_id:
            test_case_list = SourcesData.get_api_test_case(is_dict=False, id=case_id)
        elif case_name:
            test_case_list = SourcesData.get_api_test_case(is_dict=False, name=case_name)
        else:
            raise PytestAutoTestError(*ERROR_MSG_0350)

        @pytest.mark.flaky(reruns=3)
        @pytest.mark.parametrize("test_case", test_case_list)
        def wrapper(self, test_case):
            test_case_model = ApiTestCaseModel.get_obj(test_case)
            log.debug(f'准备开始执行用例，数据：{test_case_model.model_dump_json()}')
            allure.dynamic.title(test_case.get('name'))
            allure.attach(test_case_model.model_dump_json(), '用例数据')
            data = ApiDataModel(
                base_data=self.data_model.base_data,
                test_case=test_case_model
            )
            try:
                func(self, data=data)
                self.ass_main(data)
                # allure.attach(self.test_data.get_all(), '缓存数据')
            except PytestAutoTestError as error:
                log.error(error.msg)
                allure.attach(error.msg, '发生已知异常')
                raise error

        return wrapper

    return decorator


def request_data(api_info_id):
    def decorator(func):

        def wrapper(self, data: ApiDataModel) -> ApiDataModel:
            log.debug(f'开始查询接口数据，ID：{api_info_id}')
            api_info_model = ApiInfoModel.get_obj(SourcesData.get_api_info(id=api_info_id))
            log.debug(f'查询到接口的数据，接口ID：{api_info_model.model_dump_json()}')
            data.request = RequestModel(
                url=api_info_model.url,
                method=MethodEnum.get_value(api_info_model.method),
                headers=api_info_model.headers if api_info_model.headers else data.base_data.headers,
                params=data.test_case.params,
                data=data.test_case.data,
                json_data=data.test_case.json_data if data.test_case.json_data is not None else api_info_model.json_data,
                file=data.test_case.file,
            )
            log.debug(f'默认准备好的请求，数据：{data.request.model_dump_json()}')
            res_args = func(self, data)
            allure.attach(str(data.request.url), 'URL')
            allure.attach(str(data.request.method), '请求方法')
            allure.attach(str(data.request.headers), '请求头')
            if data.request.params:
                allure.attach(json.dumps(data.request.params, ensure_ascii=False), '参数')
            if data.request.data:
                allure.attach(json.dumps(data.request.data, ensure_ascii=False), '表单')
            if data.request.json_data:
                allure.attach(json.dumps(data.request.json_data, ensure_ascii=False), 'JSON')
            if data.request.file:
                allure.attach(str(data.request.file), '文件')
            allure.attach(str(data.response.status_code), '响应状态码')
            allure.attach(str(data.response.response_time * 1000), '响应时间（毫秒）')
            allure.attach(data.response.response_text, '响应结果')
            return res_args

        return wrapper

    return decorator


def timer(func):
    @functools.wraps(func)
    def swapper(self, request_model: RequestModel) -> ResponseModel:
        start = time.time()
        response: Response = func(self, request_model)
        response_time = time.time() - start
        if response_time > REQUEST_TIMEOUT_FAILURE_TIME:
            log.error(
                f"\n{'=' * 100}\n"
                f"测试用例执行时间较长，请关注.\n"
                f"函数运行时间: {response_time} ms\n"
                f"测试用例相关数据: {response}\n"
                f"{'=' * 100}")
        try:
            response_dict = response.json()
        except json.JSONDecodeError as error:
            response_dict = {
                'error_msg': '您可以检查返回的值是否是json，如果不是，就不要使用response_dict',
                'error': str(error)
            }
        formatted_response = ''.join(response.text.split())
        log.debug(f'请求的结果，response：{formatted_response}')
        return ResponseModel(
            url=response.url,
            status_code=response.status_code,
            method=request_model.method,
            headers=response.headers,
            response_text=formatted_response,
            response_dict=response_dict,
            response_time=response_time,
            content=response.content
        )

    return swapper


def log_decorator(func):
    @functools.wraps(func)
    def swapper(self, data: ApiDataModel) -> ApiDataModel:
        data = func(self, data)
        log.debug(f'用例执行完成，整个响应体：{data.response.model_dump()}')
        if PRINT_EXECUTION_RESULTS:
            _log_msg = f"\n{'=' * 200}\n" \
                       f"用例标题: {data.test_case.name}\n" \
                       f"请求路径: {data.response.url}\n" \
                       f"请求方式: {data.response.method}\n" \
                       f"请 求 头:  {data.request.headers}\n"
            if data.request.params is not None:
                _log_msg += f"请求params：{data.request.params}\n"
            if data.request.data is not None:
                _log_msg += f"请求data：{data.request.data}\n"
            if data.request.json_data is not None:
                _log_msg += f"请求json：{data.request.json_data}\n"
            if data.request.file is not None:
                _log_msg += f"请求文件：{data.request.file}\n"
            _log_msg += f"Http状态码: {data.response.status_code}\n" \
                        f"接口响应时长: {data.response.response_time} ms\n" \
                        f"接口响应内容: {data.response.response_text}\n" \
                        f"{'=' * 200}"
            if data.response.status_code == 200 or data.response.status_code == 300:
                log.info(_log_msg)
            else:
                log.error(_log_msg)
        return data

    return swapper
