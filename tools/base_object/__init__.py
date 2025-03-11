# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description:
# @Time   : 2023-07-15 11:57
# @Author : 毛鹏
from tools.base_object.web.browser import PlaywrightBrowser
from tools.base_object.web.customization import PlaywrightCustomization
from tools.base_object.web.element import PlaywrightElement
from tools.base_object.web.input_device import PlaywrightDeviceInput
from tools.base_object.web.page import PlaywrightPage


class WebDevice(PlaywrightBrowser, PlaywrightElement, PlaywrightPage, PlaywrightDeviceInput, PlaywrightCustomization):
    pass
