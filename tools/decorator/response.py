# -*- coding: utf-8 -*-
# @Description:
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import functools
import json

import allure
import time
from requests.models import Response

from config.config import PRINT_EXECUTION_RESULTS, REQUEST_TIMEOUT_FAILURE_TIME
from models.api_model import ApiDataModel, ResponseDataModel, CaseGroupModel
from models.api_model import TestCaseModel
from tools.database.sql_statement import sql_statement_3
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
            sql_handler = SQLiteHandler()
            query: list = sql_handler.execute_sql(sql_statement_3, (case_id,))
            if not query:
                raise '用例ID查询为空，请检查sql是否可以查到用例数据'
            query: dict = query[0]
            allure.attach(json.dumps(query), '查询用例数据')
            func(*args, **kwargs, data=ApiDataModel(
                test_case_id=case_id,
                project=query.get('project'),
                test_case_data=TestCaseModel.get_obj(query)))

        return wrapper

    return decorator


def request_data(func):
    """
    处理请求的数据和结果，写入allure报告
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> ApiDataModel:
        data: ApiDataModel = args[1]
        res_args = func(*args, **kwargs)

        # 处理后置allure报告
        allure.attach(str(sql), f'api_info')
        allure.attach(str(group.request.url), f'{api_info.name}->url')
        allure.attach(str(group.request.headers), f'{api_info.name}->请求头')

        allure.attach(f"参数A: {group.request.data}{group.request.params}{group.request.json_data}",
                      f'{api_info.name}->请求参数')
        allure.attach(str(group.response.status_code), f'{api_info.name}->响应状态码')
        allure.attach(str(json.dumps(group.response.response_json, ensure_ascii=False)),
                      f'{api_info.name}->响应结果')

        return res_args

    return wrapper


def timer(func):
    """
    封装统计函数执行时间装饰器
    :return:
    """

    @functools.wraps(func)
    def swapper(*args, **kwargs) -> ApiDataModel:
        s = time.time()
        res: Response = func(*args, **kwargs)
        end = time.time() - s
        # 计算时间戳毫米级别，如果时间大于number，则打印 函数名称 和运行时间
        if end > REQUEST_TIMEOUT_FAILURE_TIME:
            WARNING.logger.error(
                f"\n{'=' * 100}\n"
                "测试用例执行时间较长，请关注.\n"
                "函数运行时间: %s ms\n"
                "测试用例相关数据: %s\n"
                f"{'=' * 100}"
                , end, res)
        data: ApiDataModel = args[1]
        data.db_is_ass = args[0].data_model.db_is_ass
        group: CaseGroupModel = data.requests_list[data.step]
        group.response_time = end
        if res.text == '' or res.text is None:
            # raise ResponseError('响应结果为空，用例失败！')
            assert False
        try:
            da = res.json()
        except json.JSONDecodeError:
            da = res.text
        group.response = ResponseDataModel(url=res.url,
                                           status_code=res.status_code,
                                           method=res.request.method,
                                           headers=res.headers,
                                           body=group.request.data,
                                           encoding=res.encoding,
                                           content=res.content,
                                           text=res.text,
                                           response_json=da)

        return args[1]

    return swapper


def log_decorator(func):
    """
    封装日志装饰器, 打印请求信息
    :return:
    """

    @functools.wraps(func)
    def swapper(*args, **kwargs) -> tuple[ApiDataModel, dict]:
        res, response_dict = func(*args, **kwargs)
        # 判断日志开关为开启状态
        group: CaseGroupModel = res.requests_list[res.step]

        if PRINT_EXECUTION_RESULTS:
            _log_msg = f"\n{'=' * 100}\n" \
                       f"用例标题: {res.test_case_data.case_name}\n" \
                       f"请求路径: {group.request.url}\n" \
                       f"请求方式: {group.request.method}\n" \
                       f"请求头:   {group.request.headers}\n" \
                       f"请求内容: {group.request.json_data}{group.request.params}{group.request.data}\n" \
                       f"接口响应内容: {group.response.text}\n" \
                       f"接口响应时长: {group.response_time} ms\n" \
                       f"Http状态码: {group.response.status_code}\n" \
                       f"{'=' * 100}"
            if group.response.status_code == 200 or group.response.status_code == 300:
                INFO.logger.info(_log_msg)
            else:
                # 失败的用例，控制台打印红色
                ERROR.logger.error(_log_msg)
        return res, response_dict

    return swapper
