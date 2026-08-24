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
        test_data=test_data,
        settings=settings,
    )
    element = web_obj.element("username_input")
"""
import os

from mangoautomation.uidrives import SyncWebDevice, BaseData
from mangoautomation.uidrives.web import SyncWebAssertion
from playwright.sync_api import Locator

from core.ui.element_repository import configured_element_repository
from core.ui.element_runtime import element_runtime
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
            settings,
    ):
        self.test_data = test_data
        self.base_data = base_data
        self.project_name = project_name
        self.module_name = module_name
        self.page_name = page_name
        self.web_ass = SyncWebAssertion(self.base_data)
        super().__init__(base_data)
        self.element_repository = configured_element_repository(
            settings,
            module_name=module_name,
            page_name=page_name,
        )
        self.named_elements = element_runtime(base_data, self.element_repository, settings)

    def element(self, ele_name: str, is_count=True) -> Locator:
        """
        获取页面元素

        @param ele_name: 元素名称
        @param is_count: 是否检查元素个数
        @return: Locator 对象
        """
        locator = self.named_elements.locator(ele_name)
        if is_count and locator.count() < 1:
            raise LookupError(f"元素【{ele_name}】未找到")
        return locator

    def element_action(self, ele_name: str, method: str, params: dict | None = None):
        """Execute a Feishu/local named element through ElementModel."""
        return self.named_elements.execute(ele_name, method, params)

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
                       project_dir.download(), 'storage_state.json')):
        """设置 cookie，如果文件不存在则跳过"""
        if not os.path.isfile(storage_state_path):
            return
        with open(storage_state_path, 'r') as f:
            file_state = f.read()
        self.w_set_cookie(file_state)
