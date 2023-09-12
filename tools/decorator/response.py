# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import json

import allure
from pydantic import BaseModel
from requests.models import Response

from models.api_model import ApiInfoModel
from models.api_model import TestCaseModel
from project import TEST_PROJECT_MYSQL


def is_args_contain_base_model(*args):
    for arg in args:
        if isinstance(arg, BaseModel):
            return True
    return False


def around(api_id: int):
    """
    统一处理请求参数和响应
    :param api_id: 接口名称
    :return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs) -> Response:
            sql = f'select * FROM aigc_AutoTestPlatform.api_info WHERE id = {api_id};'
            query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
            api_info = ApiInfoModel(**query)
            res_args: tuple[Response, str, dict] = func(api_info=api_info, *args, **kwargs)
            response: Response = res_args[0]

            allure.attach(str(sql), f'api_info')
            allure.attach(str(res_args[1]), f'{api_info.name}->url')
            allure.attach(str(res_args[2]), f'{api_info.name}->请求头')
            arg1 = ''
            arg2 = ''
            for arg in args[1:]:
                if isinstance(arg, BaseModel):
                    arg1 += str(arg.json())
                else:
                    arg2 += f', {arg}'
            allure.attach(f"参数A: {arg1 + arg2}\n"
                          f"参数B: {', '.join(f'{key}={val}' for key, val in kwargs.items())}",
                          f'{api_info.name}->请求参数')
            allure.attach(str(response.status_code), f'{api_info.name}->响应状态码')
            allure.attach(str(json.dumps(response.json(), ensure_ascii=False)), f'{api_info.name}->响应结果')
            return response

        return wrapper

    return decorator


def testdata(case_id: int, _is: bool = False):
    """

    @param case_id: 用例ID或接口ID
    @param _is: false=用例ID，true等于是接口ID
    @return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            sql = f'select * FROM test_case WHERE id = {case_id};'
            if _is:
                sql = f'select * FROM test_case WHERE api_id = {case_id};'
            query: dict = TEST_PROJECT_MYSQL.execute_query(sql)
            test_case = [TestCaseModel(**i) for i in query]
            allure.attach(str(sql), f'test_case')
            func(*args, **kwargs, test_case=test_case)

        return wrapper

    return decorator

# def api_and_case(api_path: str):
#     """
#     统一处理用例数据
#     :param api_path: apipath
#     :return:
#     """
#
#     def decorator(func):
#         def wrapper(*args, **kwargs) -> Response:
#             sql = f'select a.`name` as caseName,a.case_data as caseData,b.`name` as apiName, ' \
#                   f'b.url,a.case_ass as caseAss,type,method,headers ' \
#                   f'from test_case a INNER JOIN api_info b ON a.api_id=b.id where url="{api_path}";'
#             query: list[dict] = TEST_PROJECT_MYSQL.execute_query(sql)
#             api_and_case_info = listApiAndCaseInfo(case_list=query)
#             # allure.attach(str(test_case.json()))
#
#             func(*args, **kwargs, api_and_case_info=api_and_case_info)
#
#         return wrapper
#
#     return decorator
