from tools.obtain_test_data import ObtainTestData
from playwright.async_api import Page, BrowserContext

from tools.base_page.web.browser import PlaywrightBrowser
from tools.base_page.web.customization import PlaywrightCustomization
from tools.base_page.web.element import PlaywrightElement
from tools.base_page.web.input_device import PlaywrightDeviceInput
from tools.base_page.web.page import PlaywrightPage


class WebDevice(PlaywrightBrowser, PlaywrightElement, PlaywrightPage, PlaywrightDeviceInput, PlaywrightCustomization):

    def __init__(self, page: Page, context: BrowserContext, test_data: ObtainTestData):
        self.page: Page = page
        self.context: BrowserContext = context
        self.test_data = test_data
