import asyncio
from typing import Optional

from playwright.async_api import Page, BrowserContext

from tools.base_page.web.browser import PlaywrightBrowser
from tools.base_page.web.element import PlaywrightElement
from tools.base_page.web.input_device import PlaywrightDeviceInput
from tools.base_page.web.page import PlaywrightPage
from tools.data_processor import DataProcessor
from tools.log_collector import log


class WebDevice(PlaywrightBrowser, PlaywrightElement, PlaywrightPage, PlaywrightDeviceInput):

    def __init__(self, page: Page, context: BrowserContext, data_processor: DataProcessor):
        self.page: Page = page
        self.context: BrowserContext = context
        self.data_processor = data_processor
        # self.context_page = context_page
        # self.initialized_event = asyncio.Event()

    def initialize(self):
        asyncio.run(self.setup())

    async def setup(self):
        await self.get_page_context(self.context_page)

    async def get_page_context(self, context_page):
        async for context in context_page:
            self.context = context
            self.page = await context.new_page()
            log.warning(f"类型是2：{str(type(self.context))}")
            log.warning(f"类型是3：{str(type(self.page))}")
