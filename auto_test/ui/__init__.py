# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 10:49
# @Author : 毛鹏
import asyncio

import pytest

from enums.ui_enum import BrowserTypeEnum
from models.ui_model import WEBConfigModel
from tools.base_page.web.new_browser import NewBrowser
from tools.data_processor import DataProcessor
from tools.log_collector import log

global_data_processor = DataProcessor()


@pytest.fixture(scope='function')
async def setup_context_page():
    data = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
    return await data.new_context_page()


async def setup_context_page1():
    data = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
    context, page = await data.new_context_page()
    log.warning(str(type(context)))
    log.warning(str(type(page)))
    try:
        return context, page
    finally:
        await context.close()
        await page.close()


if __name__ == '__main__':
    asyncio.run(setup_context_page1())
