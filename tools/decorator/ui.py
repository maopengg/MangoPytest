# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-14 14:05
# @Author : 毛鹏
import allure
import pytest
from mangoautomation.uidrive import DriverObject
from mangoautomation.uidrives import BaseData

from enums.ui_enum import BrowserTypeEnum
from exceptions import PytestAutoTestError
from exceptions.error_msg import ERROR_MSG_0350
from models.ui_model import UiDataModel, UiTestCaseModel
from tools import project_dir
from tools.log import log

driver_object = DriverObject(log)
driver_object.set_web(web_type=BrowserTypeEnum.CHROMIUM.value, web_max=True)


def case_data(case_id: int | list[int] | None = None, case_name: str | list[str] | None = None):
    def decorator(func):
        log.debug(f'开始查询用例，用例ID:{case_id} 用例名称：{case_name}')
        from sources import SourcesData
        if case_id:
            test_case_list = SourcesData.get_ui_test_case(is_dict=False, id=case_id)
        elif case_name:
            test_case_list = SourcesData.get_ui_test_case(is_dict=False, name=case_name)
        else:
            raise PytestAutoTestError(*ERROR_MSG_0350)

        @pytest.mark.parametrize("test_case", test_case_list)
        def wrapper(self, test_case):
            allure.dynamic.title(test_case.get('name'))
            context, page = driver_object.web.new_web_page()
            base_data = BaseData(self.test_data, log)
            if base_data.page is None or base_data.context is None:
                base_data.set_page_context(page, context)
            base_data.set_file_path(project_dir.download(), project_dir.screenshot())

            data = UiDataModel(test_case=UiTestCaseModel.get_obj(test_case))
            try:
                func(self, base_data, data=data)
            except Exception as error:
                log.error(f'错误类型:{type(error)}，{error}')
                context.close()
                page.close()
                raise error
            context.close()
            page.close()

        return wrapper

    return decorator
