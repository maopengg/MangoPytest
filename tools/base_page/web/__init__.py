from playwright.async_api import Page, BrowserContext

from tools.base_page.web.input_device import PlaywrightDeviceInput
from tools.base_page.web.element import PlaywrightElement
from tools.base_page.web.browser import PlaywrightBrowser
from tools.base_page.web.page import PlaywrightPage
from tools.data_processor import DataProcessor


class WebDevice(PlaywrightBrowser, PlaywrightElement, PlaywrightPage, PlaywrightDeviceInput):

    def __init__(self, page: Page, context: BrowserContext, data_processor: DataProcessor):
        self.page: Page = page
        self.context: BrowserContext = context
        self.data_processor = data_processor
