# -*- coding: utf-8 -*-
# @Description:
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import functools
import json
import time

import allure
from requests.models import Response

from enums.api_enum import MethodEnum
from exceptions import PytestAutoTestError
from exceptions.api_exception import CaseParameterError
from exceptions.error_msg import ERROR_MSG_0334
from models.api_model import ApiDataModel, ResponseModel, TestCaseModel, RequestModel
from settings.settings import PRINT_EXECUTION_RESULTS, REQUEST_TIMEOUT_FAILURE_TIME
from tools.database.sql_statement import sql_statement_4
from tools.database.sqlite_handler import SQLiteHandler
from tools.logging_tool.log_control import ERROR, WARNING, INFO


def case_data(case_id: int):
    """
    1.查询测试数据，写入allure报告
    2.断言结果写入allure报告
    @param case_id: 用例ID或接口ID
    @return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            test_case_dict: dict = SQLiteHandler().execute_sql(sql_statement_4, (case_id,))[0]
            allure.attach(json.dumps(test_case_dict, ensure_ascii=False), '查询用例数据')
            try:
                func(
                    *args,
                    **kwargs,
                    data=ApiDataModel(base_data=args[0].data_model.base_data_model,
                                      test_case=TestCaseModel.get_obj(test_case_dict))
                )
            except PytestAutoTestError as error:
                ERROR.logger.error(error.msg)
                allure.attach(error.msg, '执行中断异常')
                raise error

        return wrapper

    return decorator


def request_data(func):
    """
    处理请求的数据和结果，写入allure报告
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> ApiDataModel:
        data: ApiDataModel = kwargs.get('data')

        data.request = RequestModel(
            url=data.test_case.url,
            method=MethodEnum.get_value(data.test_case.method),
            headers=data.base_data.headers,
            params=data.test_case.params,
            data=data.test_case.data,
            json_data=data.test_case.json_data,
            file=data.test_case.file,
        )
        try:
            res_args = func(*args, **kwargs)
        except TypeError:
            raise CaseParameterError(*ERROR_MSG_0334)
        # 处理后置allure报告
        allure.attach(str(data.request.url), 'url')
        allure.attach(str(data.request.method), '请求方法')
        allure.attach(str(data.request.headers), '请求头')
        if data.request.params:
            allure.attach(json.dumps(data.request.params, ensure_ascii=False), '参数')
        if data.request.data:
            allure.attach(json.dumps(data.request.data, ensure_ascii=False), '表单')
        if data.request.json_data:
            allure.attach(json.dumps(data.request.json_data, ensure_ascii=False), 'json')
        if data.request.file:
            allure.attach(json.dumps(data.request.file, ensure_ascii=False), '文件')

        allure.attach(str(data.response.status_code), '响应状态码')
        allure.attach(json.dumps(data.response.response_dict, ensure_ascii=False), '响应结果')

        return res_args

    return wrapper


def timer(func):
    """
    封装统计函数执行时间装饰器
    :return:
    """

    @functools.wraps(func)
    def swapper(*args, **kwargs) -> ApiDataModel:
        start = time.time()
        response: Response = func(*args, **kwargs)
        response_time = time.time() - start
        # 计算时间戳毫米级别，如果时间大于number，则打印 函数名称 和运行时间
        if response_time > REQUEST_TIMEOUT_FAILURE_TIME:
            WARNING.logger.error(
                f"\n{'=' * 100}\n"
                "测试用例执行时间较长，请关注.\n"
                "函数运行时间: %s ms\n"
                "测试用例相关数据: %s\n"
                f"{'=' * 100}"
                , response_time, response)
        try:
            response_dict = response.json()
        except json.JSONDecodeError:
            response_dict = '序列化json失败'

        data: ApiDataModel = args[1]
        data.response = ResponseModel(url=response.url,
                                      status_code=response.status_code,
                                      method=data.request.method,
                                      headers=response.headers,
                                      response_text=response.text,
                                      response_dict=response_dict,
                                      response_time=response_time
                                      )

        return data

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
                INFO.logger.info(_log_msg)
            else:
                ERROR.logger.error(_log_msg)
        return data

    return swapper
