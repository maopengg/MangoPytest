# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 其他测试装饰器
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
其他测试装饰器模块

包含：
- case_data: 其他类型用例数据装饰器
"""

import allure
import pytest

from exceptions import PytestAutoTestError
from exceptions.error_msg import ERROR_MSG_0350
from models.other_model import OtherDataModel, OtherTestCaseModel
from tools.log import log


def case_data(case_id: int | list[int] | None = None, case_name: str | list[str] | None = None):
    """
    其他类型用例数据装饰器

    Args:
        case_id: 用例ID
        case_name: 用例名称
    """

    def decorator(func):
        log.debug(f'开始查询用例：{case_id if case_id else case_name}')
        from sources import SourcesData
        if case_id:
            test_case_list = SourcesData.get_other_test_case(is_dict=False, id=case_id)
        elif case_name:
            test_case_list = SourcesData.get_other_test_case(is_dict=False, name=case_name)
        else:
            raise PytestAutoTestError(*ERROR_MSG_0350)

        @pytest.mark.flaky(reruns=3)
        @pytest.mark.parametrize("test_case", test_case_list)
        def wrapper(self, test_case):
            test_case_model = OtherTestCaseModel.get_obj(test_case)
            log.debug(f'准备开始执行用例，数据：{test_case_model.model_dump_json()}')
            allure.dynamic.title(test_case.get('name'))
            allure.attach(test_case_model.model_dump_json(), '用例数据', allure.attachment_type.JSON)
            data = OtherDataModel(
                test_case=test_case_model
            )
            try:
                func(self, data=data)
            except PytestAutoTestError as error:
                log.error(error.msg)
                allure.attach(error.msg, '发生已知异常', allure.attachment_type.TEXT)
                raise error

        return wrapper

    return decorator
