# -*- coNoneing: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import json

import allure
from pydantic import BaseModel

from auto_test.api_project import TEST_PROJECT_MYSQL
from models.api_model import ApiInfoModel, TestCaseModel, ApiDataModel, CaseGroupModel
from tools.logging_tool.log_control import ERROR


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
        def wrapper(*args, **kwargs) -> ApiDataModel:
            # 处理前置用例数据
            sql = f'select * FROM aigc_AutoTestPlatform.api_info WHERE id = {api_id};'
            query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
            api_info = ApiInfoModel.get_obj(query)
            data: ApiDataModel = args[1]
            data.db_is_ass = args[0].data_model.db_is_ass
            if len(data.requests_list) <= data.step:
                data.requests_list.append(CaseGroupModel())
            # 处理请求数据
            group: CaseGroupModel = data.requests_list[data.step]
            group.api_id, group.api_data = api_id, api_info
            group.request.method = group.request.method_list[api_info.method]
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

    return decorator


def case_data(case_id: int):
    """
    @param case_id: 用例ID或接口ID
    @return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            sql = f'select * FROM test_case WHERE id = {case_id};'
            allure.attach(str(sql), f'test_case')
            query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
            if len(query) < 1:
                ERROR.logger.error('用例ID查询为空，请检查sql是否可以查到用例数据！')

            return func(*args, **kwargs, data=ApiDataModel(
                test_case_id=case_id,
                project=query.get('project'),
                test_case_data=TestCaseModel.get_obj(query)))

        return wrapper

    return decorator
