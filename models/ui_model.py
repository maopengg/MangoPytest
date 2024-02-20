# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:11
# @Author : 毛鹏
from pydantic import BaseModel


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
