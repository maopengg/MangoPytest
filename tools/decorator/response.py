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
from models.api_model import ApiDataModel, ResponseModel, TestCaseModel, RequestModel, ApiInfoModel
from settings.settings import PRINT_EXECUTION_RESULTS, REQUEST_TIMEOUT_FAILURE_TIME
from tools.log import log


def case_data(case_id: int | list[int] | None = None, case_name: str | list[str] | None = None):
    def decorator(func):
        from sources import SourcesData
        if isinstance(case_id, int):
            case_id_list = [case_id]
        else:
            case_id_list = case_id
        if isinstance(case_name, str):
            case_name_list = [case_name]
        else:
            case_name_list = case_name

        test_case_list: list = []
        if case_id_list:
            for i in case_id_list:
                test_case_dict: dict = SourcesData \
                    .api_test_case[SourcesData.api_test_case['id'] == i] \
                    .squeeze() \
                    .to_dict()
                test_case_list.append(test_case_dict)
        elif case_name_list:
            for i in case_name_list:
                test_case_dict: dict = SourcesData \
                    .api_test_case[SourcesData.api_test_case['name'] == i] \
                    .squeeze() \
                    .to_dict()
                test_case_list.append(test_case_dict)
        else:
            raise PytestAutoTestError(*ERROR_MSG_0350)

        @pytest.mark.parametrize("test_case", test_case_list)
        def wrapper(self, test_case):
            allure.title(test_case.get('name', '默认名称'))
            allure.attach(json.dumps(test_case, ensure_ascii=False), '用例数据')
            data = ApiDataModel(base_data=self.data_model.base_data_model, test_case=TestCaseModel.get_obj(test_case))
            try:
                func(self, data=data)
                self.ass_main(data)
            except PytestAutoTestError as error:
                log.error(error.msg)
                allure.attach(error.msg, '发生已知异常')
                raise error
            except Exception as error:
                log.error(error)
                allure.attach(error, '发生未知异常')
                raise error

        return wrapper

    return decorator


def request_data(api_info_id):
    """
    处理请求的数据和结果，写入allure报告
    :return:
    """

    def decorator(func):

        # @functools.wraps(func)
        def wrapper(*args, **kwargs) -> ApiDataModel:
            data: ApiDataModel = kwargs.get('data')
            if len(args) == 2:
                data: ApiDataModel = args[1]
            from sources import SourcesData
            api_info_dict: dict = SourcesData \
                .api_info[SourcesData.api_info['id'] == api_info_id] \
                .squeeze() \
                .to_dict()
            api_info_model = ApiInfoModel.get_obj(api_info_dict)
            log.debug(f"{api_info_id}-----{api_info_model.model_dump_json()}")
            data.request = RequestModel(
                url=api_info_model.url,
                method=MethodEnum.get_value(api_info_model.method),
                headers=api_info_model.headers if api_info_model.headers else data.base_data.headers,
                params=data.test_case.params,
                data=data.test_case.data,
                json_data=data.test_case.json_data,
                file=data.test_case.file,
            )
            log.debug(f'请求调用http之前的request：{data.request.model_dump_json()}')
            res_args = func(*args, **kwargs)
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
                allure.attach(json.dumps(data.request.file, ensure_ascii=False), '文件')
            allure.attach(str(data.response.status_code), '响应状态码')
            allure.attach(str(data.response.response_time * 1000), '响应时间（毫秒）')
            allure.attach(json.dumps(data.response.response_dict, ensure_ascii=False), '响应结果')

            return res_args

        return wrapper

    return decorator


def timer(func):
    """
    封装统计函数执行时间装饰器
    :return:
    """

    @functools.wraps(func)
    def swapper(*args, **kwargs) -> ResponseModel:
        start = time.time()
        response: Response = func(*args, **kwargs)
        response_time = time.time() - start
        # 计算时间戳毫米级别，如果时间大于number，则打印 函数名称 和运行时间
        if response_time > REQUEST_TIMEOUT_FAILURE_TIME:
            log.error(
                f"\n{'=' * 100}\n"
                f"测试用例执行时间较长，请关注.\n"
                f"函数运行时间: {response_time} ms\n"
                f"测试用例相关数据: {response}\n"
                f"{'=' * 100}")
        try:
            response_dict = response.json()
        except json.JSONDecodeError:
            response_dict = '您可以检查返回的值是否是json，如果不是，就不要使用response_dict'

        data: RequestModel = args[1]
        return ResponseModel(url=response.url,
                             status_code=response.status_code,
                             method=data.method,
                             headers=response.headers,
                             response_text=response.text,
                             response_dict=response_dict,
                             response_time=response_time
                             )

    return swapper


def log_decorator(func):
    """
    封装日志装饰器, 打印请求信息
    :return:
    """

    @functools.wraps(func)
    def swapper(*args, **kwargs) -> ApiDataModel:
        data = func(*args, **kwargs)
        # 判断日志开关为开启状态
        if PRINT_EXECUTION_RESULTS:
            _log_msg = f"\n{'=' * 100}\n" \
                       f"用例标题: {data.test_case.name}\n" \
                       f"请求路径: {data.response.url}\n" \
                       f"请求方式: {data.response.method}\n" \
                       f"请求头:   {data.request.headers}\n" \
                       f"请求内容: {data.request.params}{data.request.json_data}{data.request.data}\n" \
                       f"接口响应内容: {data.response.response_text}\n" \
                       f"接口响应时长: {data.response.response_time} ms\n" \
                       f"Http状态码: {data.response.status_code}\n" \
                       f"{'=' * 100}"
            if data.response.status_code == 200 or data.response.status_code == 300:
                log.info(_log_msg)
            else:
                log.error(_log_msg)
        return data

    return swapper
