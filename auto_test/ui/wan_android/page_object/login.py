# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 11:04
# @Author : 毛鹏
from urllib.parse import urljoin

from playwright.sync_api import Page, BrowserContext

from auto_test.ui.wan_android import WanAndroidDataModel
from tools.base_page import BasePage


class LoginPage(BasePage):
    """
    登录页面
    """

    def __init__(self, context_page: tuple[BrowserContext, Page], data_model: WanAndroidDataModel):
        project_id = 4
        module_name = '登录'
        super().__init__(project_id, module_name, context_page, data_model.data_processor)
        self.url = urljoin(data_model.base_data_model.host, '/index')

    # 查询操作
    async def login(self, username: str, password: str):
        await self.w_click(await self.element('登录按钮'))
        await self.w_input(await self.element('用户名'), username)
        await self.w_input(await self.element('密码'), password)
        await self.w_click(await self.element('登录'))


if __name__ == '__main__':
    from tools.base_page.web.new_browser import NewBrowser
    from enums.ui_enum import BrowserTypeEnum
    from models.ui_model import WEBConfigModel

    url = "https://wanandroid.com/index"
    data = NewBrowser(WEBConfigModel(browser_type=BrowserTypeEnum.CHROMIUM))
    login_page = LoginPage(data.new_context_page(), WanAndroidDataModel())
    login_page.w_goto(login_page.url)
    login_page.login('maopeng', '729164035')
