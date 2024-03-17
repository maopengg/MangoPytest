# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:11
# @Author : 毛鹏
from pydantic import BaseModel

from enums.ui_enum import ElementExpEnum, BrowserTypeEnum


class WEBConfigModel(BaseModel):
    """ web启动配置 """
    browser_type: BrowserTypeEnum
    browser_port: str | None = None
    browser_path: str | None = None
    is_headless: bool = False


class AndroidConfigModel(BaseModel):
    equipment: str
    package_name: str


class ElementModel(BaseModel):
    id: int
    ele_name: str
    nth: int | None = None
    sleep: int | None = None
    iframe: list[str] | None = None
    method: ElementExpEnum
    locator: str
    name: str | None = None
    exact: bool | None = None
    has_text: str | None = None
    has: str | None = None
    locator2: str | None = None
