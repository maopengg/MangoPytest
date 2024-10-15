# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:11
# @Author : 毛鹏
from mangokit import MysqlConingModel, MysqlConnect
from pydantic import BaseModel, ConfigDict

from enums.ui_enum import ElementExpEnum, BrowserTypeEnum


class WEBConfigModel(BaseModel):
    """ web启动配置 """
    browser_type: BrowserTypeEnum
    browser_port: str | None = None
    browser_path: str | None = None
    is_headless: bool = False


class AndroidConfigModel(BaseModel):
    equipment: str


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


class UiBaseDataModel(BaseModel):
    """
        每个自动化的项目要在这里设置全局通用的变量，如域名，测试环境，请求头等信息，后面在发生真正请求时，会使用这这里面的信息
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    test_object: dict  # 测试对象表
    project: dict  # 项目表
    host: str  # 域名
    is_database_assertion: bool
    mysql_config_model: MysqlConingModel | None = None
    mysql_connect: MysqlConnect | None = None
    other_data: dict | None = None  # 其他数据
