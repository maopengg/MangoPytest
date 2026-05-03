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
    from core.ui import WebBaseObject
    
    web_obj = WebBaseObject(
        project_name="demo",
        module_name="login",
        page_name="login_page",
        base_data=base_data,
        test_data=test_data
    )
    element = web_obj.element("username_input")
"""
import os
import random
import re

import allure
from mangoautomation.enums import ElementOperationEnum
from mangoautomation.mangos import SyncWebAssertion
from mangoautomation.uidrive import BaseData, SyncWebDevice
from mangotools.decorator import sync_retry
from mangotools.enums import StatusEnum
from playwright.sync_api import Locator

from core.exceptions import PytestAutoTestError, ERROR_MSG_0001
from core.sources import SourcesData
from core.utils import log, project_dir
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
        self.base_data = base_data
        self.project_name = project_name
        self.module_name = module_name
        self.page_name = page_name
        self.web_ass = SyncWebAssertion(self.base_data)
        super().__init__(base_data)
        d = re.DEBUG
        self.set_cookie()

    @sync_retry()
    def element(self, ele_name: str, is_count=True) -> Locator:
        """
        获取页面元素

        @param ele_name: 元素名称
        @param is_count: 是否检查元素个数
        @return: Locator 对象
        """
        element_dict: dict = SourcesData.get_ui_element(
            项目名称=self.project_name,
            模块名称=self.module_name,
            页面名称=self.page_name,
            元素名称=ele_name,
        )
        element_list = [{
            'method': element_dict.get('定位方式1'),
            'locator': self.test_data.replace(element_dict.get('表达式1')),
            'nth': element_dict.get('下标1')
        }]
        if element_dict.get('定位方式2') and element_dict.get('表达式2'):
            element_list.append({
                'method': element_dict.get('定位方式2'),
                'locator': self.test_data.replace(element_dict.get('表达式2')),
                'nth': element_dict.get('下标2')
            })
        if element_dict.get('定位方式3') and element_dict.get('表达式3'):
            element_list.append({
                'method': element_dict.get('定位方式3'),
                'locator': self.test_data.replace(element_dict.get('表达式3')),
                'nth': element_dict.get('下标3')
            })
        element_list = self.test_data.replace(element_list)
        ran = random.randint(0, len(element_list) - 1)
        loc, count, text = self.web_find_element(
            ele_name,
            ElementOperationEnum.OPE.value,
            element_list[ran].get('method'),
            element_list[ran].get('locator'),
            element_list[ran].get('nth'),
            StatusEnum.FAIL.value,
        )
        allure.attach(
            f'元素表达式：{element_list[ran].get("locator")}\n'
            f'元素定位方法：{element_list[ran].get("method")}\n'
            f'元素下标：{element_list[ran].get("nth")}\n'
            f'元素文本内容：{text}\n'
            f'元素个数：{count}',
            ele_name,
            allure.attachment_type.TEXT
        )
        if count < 1 and is_count:
            raise PytestAutoTestError(*ERROR_MSG_0001, value=(ele_name, loc))
        log.debug(f'元素【{ele_name}】获取到的信息：{loc.count()}, {count}, {text}')
        return loc

    def w_contains_text(self, text: str) -> bool:
        """
        检查页面是否包含指定文本

        @param text: 要检查的文本
        @return: 是否包含
        """
        try:
            # 使用 Playwright 的 locator 来检查文本
            locator = self.base_data.page.locator(f'text={text}')
            return locator.count() > 0
        except Exception as e:
            log.debug(f'检查文本【{text}】时出错: {e}')
            return False

    def set_cookie(self,
                   storage_state_path: str = os.path.join(
                       project_dir.root_path(), 'auto_tests', 'qfei_contract_ui', 'upload', 'storage_state.json')):
        """设置 cookie，如果文件不存在则跳过"""
        if not os.path.isfile(storage_state_path):
            return
        with open(storage_state_path, 'r') as f:
            file_state = f.read()
        self.w_set_cookie(file_state)