# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-21 15:09
# @Author : 毛鹏
import random
import re
import time

import allure
from mangoautomation.enums import ElementOperationEnum
from mangoautomation.uidrive import BaseData, SyncWebDevice
from mangotools.decorator import sync_retry
from mangotools.enums import StatusEnum
from playwright.async_api import Page, BrowserContext
from playwright.sync_api import Locator

from exceptions import PytestAutoTestError, ERROR_MSG_0001
from sources import SourcesData
from tools.log import log
from tools.obtain_test_data import ObtainTestData


class WebBaseObject(SyncWebDevice):

    def __init__(self,
                 project_name: str,
                 module_name: str,
                 page_name: str,
                 base_data: BaseData,
                 test_data: ObtainTestData,
                 ):
        self.test_data = test_data
        self.project_name = project_name
        self.module_name = module_name
        self.page_name = page_name
        super().__init__(base_data)
        d = re.DEBUG
        self.max_retry = 20

    @sync_retry()
    def element(self, ele_name: str, is_count=True) -> Locator:
        element_dict: dict = SourcesData.get_ui_element(
            project_name=self.project_name,
            module_name=self.module_name,
            page_name=self.page_name,
            ele_name=ele_name,
        )
        element_list = [{
            'method': element_dict.get('method1'),
            'locator': self.test_data.replace(element_dict.get('locator1')),
            'nth': element_dict.get('nth1')
        }]
        if element_dict.get('method2') and element_dict.get('locator2'):
            element_list.append({
                'method': element_dict.get('method2'),
                'locator': self.test_data.replace(element_dict.get('locator2')),
                'nth': element_dict.get('nth2')
            })
        if element_dict.get('method3') and element_dict.get('locator3'):
            element_list.append({
                'method': element_dict.get('method3'),
                'locator': self.test_data.replace(element_dict.get('locator3')),
                'nth': element_dict.get('nth3')
            })
        ran = random.randint(0, len(element_list) - 1)
        loc, count, text = self.web_find_element(
            ele_name,
            ElementOperationEnum.OPE.value,
            element_list[ran].get('method'),
            element_list[ran].get('locator'),
            element_list[ran].get('nth'),
            StatusEnum.FAIL.value,
        )
        if count < 1 and is_count:
            raise PytestAutoTestError(*ERROR_MSG_0001)
        allure.attach(
            f'元素表达式：{element_list[ran].get("locator")}\n'
            f'元素定位方法：{element_list[ran].get("method")}\n'
            f'元素下标：{element_list[ran].get("nth")}\n'
            f'元素文本内容：{text}\n'
            f'元素个数：{count}'
            , ele_name)
        log.debug(f'元素【{ele_name}】获取到的信息：{loc.count()}, {count}, {text}')
        return loc
