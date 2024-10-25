# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-14 14:05
# @Author : 毛鹏
import allure
import pytest

from enums.ui_enum import BrowserTypeEnum
from models.ui_model import WEBConfigModel
from tools.base_page.web.new_browser import NewBrowser
from tools.log import log


def case_data(title, parametrize):
    def decorator(func):
        @allure.title(title)
        @pytest.mark.parametrize("data", parametrize)
        def wrapper(self, data):
            # 根据参数数量动态选择参数
            browser = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
            setup_context_page = browser.new_context_page()
            return func(self, setup_context_page, data)

        return wrapper

    return decorator
