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
from tools.base_page.web.new_browser import NewBrowser


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
                    .ui_test_case.loc[SourcesData.api_test_case['id'] == i] \
                    .squeeze() \
                    .to_dict()
                test_case_list.append(test_case_dict)
        elif case_name_list:
            for i in case_name_list:
                test_case_dict: dict = SourcesData. \
                    ui_test_case.loc[SourcesData.api_test_case['name'] == i] \
                    .squeeze() \
                    .to_dict()
                test_case_list.append(test_case_dict)
        else:
            raise PytestAutoTestError(*ERROR_MSG_0350)

        @pytest.mark.parametrize("test_case", test_case_list)
        def wrapper(self, test_case):
            allure.dynamic.title(test_case.get('name'))
            browser = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
            context, page = browser.new_context_page()
            data = UiDataModel(base_data=self.data_model.base_data_model, test_case=UiTestCaseModel.get_obj(test_case))
            func(self, execution_context=(context, page), data=data)
            context.close()
            page.close()

        return wrapper

    return decorator
