# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:11
# @Author : 毛鹏
from pydantic import BaseModel

from enums.ui_enum import ElementExpEnum


class WEBConfigModel(BaseModel):
    """ web启动配置 """
    browser_type: int
    browser_port: str | None
    browser_path: str | None
    is_headless: int | None
    is_header_intercept: bool = False
    host: str | None = None
    project_id: int | None = None


class AndroidConfigModel(BaseModel):
    equipment: str
    package_name: str


class ElementModel(BaseModel):
    id: int
    project_id: int
    ele_name: str
    nth: int
    sleep: int
    iframe: list[str] | None = None
    method: ElementExpEnum
    loc: str
    name: str
    exact: bool | None = None
    has_text: str | None = None
    has: str | None = None
    loc2: str
