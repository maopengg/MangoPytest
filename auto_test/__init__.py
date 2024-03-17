# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 10:49
# @Author : 毛鹏
from pydantic import BaseModel
from pydantic.v1 import ConfigDict

from models.tools_model import MysqlConingModel
from tools.database.mysql_control import MySQLConnect


class ApiBaseDataModel(BaseModel):
    """
        每个自动化的项目要在这里设置全局通用的变量，如域名，测试环境，请求头等信息，后面在发生真正请求时，会使用这这里面的信息
    """
    test_object: dict  # 测试对象表
    project: dict  # 项目表
    host: str  # 域名
    headers: dict | None = None  # 请求头
    is_database_assertion: bool
    mysql_config_model: MysqlConingModel | None = None
    mysql_connect: MySQLConnect | None = None
    other_data: dict | None = None  # 其他数据

    class Config(ConfigDict):
        arbitrary_types_allowed = True


class UiBaseDataModel(BaseModel):
    """
        每个自动化的项目要在这里设置全局通用的变量，如域名，测试环境，请求头等信息，后面在发生真正请求时，会使用这这里面的信息
    """
    test_object: dict  # 测试对象表
    project: dict  # 项目表
    host: str  # 域名
    is_database_assertion: bool
    mysql_config_model: MysqlConingModel | None = None
    mysql_connect: MySQLConnect | None = None
    other_data: dict | None = None  # 其他数据

    class Config(ConfigDict):
        arbitrary_types_allowed = True
