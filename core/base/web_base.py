# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Web UI 基础对象类
# @Time   : 2025-04-21 15:09
# @Author : 毛鹏
"""
Web UI 基础对象模块

提供 Web UI 测试的基础功能：
- 元素定位
- 元素操作
- 数据替换

使用示例：
    from core.base import WebBaseObject
    
    web_obj = WebBaseObject(
        project_name="demo",
        module_name="login",
        page_name="login_page",
        base_data=base_data,
        test_data=test_data
    )
    element = web_obj.element("username_input")
"""
import random
import re

import allure
from mangoautomation.enums import ElementOperationEnum
from mangoautomation.uidrive import BaseData, SyncWebDevice
from mangotools.decorator import sync_retry
from mangotools.enums import StatusEnum
from playwright.sync_api import Locator

from core.exceptions import PytestAutoTestError, ERROR_MSG_0001
from core.sources import SourcesData
from core.utils import log
from core.utils.obtain_test_data import ObtainTestData


class WebBaseObject(SyncWebDevice):
    """
    Web UI 基础对象类
    
    封装 Web UI 测试的通用功能，继承自 SyncWebDevice
    """

    def __init__(
        self,
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

    @sync_retry()
    def element(self, ele_name: str, is_count=True) -> Locator:
        """
        获取页面元素
        
        @param ele_name: 元素名称
        @param is_count: 是否检查元素个数
        @return: Locator 对象
        """
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
            , ele_name, allure.attachment_type.TEXT)
        log.debug(f'元素【{ele_name}】获取到的信息：{loc.count()}, {count}, {text}')
        return loc
