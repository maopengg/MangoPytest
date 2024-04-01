# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 10:49
# @Author : 毛鹏
import pytest

from enums.ui_enum import BrowserTypeEnum
from models.ui_model import WEBConfigModel
from tools.base_page.web.new_browser import NewBrowser
from tools.data_processor import DataProcessor

global_data_processor = DataProcessor()


@pytest.fixture(scope='function')
def setup_context_page():
    data = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
    context, page = data.new_context_page()
    yield context, page
    context.close()
    page.close()
