# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-14 14:05
# @Author : 毛鹏
import allure
import pytest

from enums.ui_enum import BrowserTypeEnum
from exceptions import PytestAutoTestError
from exceptions.error_msg import ERROR_MSG_0350
from models.ui_model import WEBConfigModel, UiDataModel, UiTestCaseModel
from tools.base_object.web.web_object.new_browser import NewBrowser
from tools.log import log


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
            browser = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
            context, page = browser.new_context_page()
            data = UiDataModel(base_data=self.data_model.base_data, test_case=UiTestCaseModel.get_obj(test_case))
            try:
                func(self, execution_context=(context, page), data=data)
            except Exception as error:
                log.error(f'错误类型:{type(error)}，{error}')
                context.close()
                page.close()
                raise error
            context.close()
            page.close()

        return wrapper

    return decorator
