# -*- coding: utf-8 -*-
# @Description:
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import json

import allure
import pytest

from exceptions import PytestAutoTestError
from exceptions.error_msg import ERROR_MSG_0350
from models.other_model import OtherDataModel, OtherTestCaseModel
from tools.log import log


def case_data(case_id: int | list[int] | None = None, case_name: str | list[str] | None = None):
    def decorator(func):
        log.debug(f'开始查询用例，用例ID:{case_id} 用例名称：{case_name}')
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
            allure.attach(json.dumps(test_case, ensure_ascii=False), '用例数据')

            data = OtherDataModel(base_data=self.data_model.base_data,
                                  test_case=test_case_model)
            try:
                func(self, data=data)
                # allure.attach(self.test_data.get_all(), '缓存数据')
            except PytestAutoTestError as error:
                log.error(error.msg)
                allure.attach(error.msg, '发生已知异常')
                raise error

        return wrapper

    return decorator
