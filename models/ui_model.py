# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-01-17 11:11
# @Author : 毛鹏
import json

from mangokit import MysqlConingModel, MysqlConnect, DataClean
from pydantic import BaseModel, ConfigDict

from enums.tools_enum import EnvironmentEnum
from enums.ui_enum import ElementExpEnum, BrowserTypeEnum
from tools.obtain_test_data import ObtainTestData


def json_serialize(data: str | None):
    try:
        if isinstance(data, str):
            return json.loads(data)
        else:
            return data
    except (json.decoder.JSONDecodeError, TypeError):
        return data


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


class UiTestCaseModel(BaseModel):
    id: int
    project_name: str
    name: str
    data: dict | list[dict] | None = None
    ass: dict | list[dict] | str | None = None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(
            id=data['id'],
            project_name=data['project_name'],
            name=data['name'],
            data=json_serialize(data.get('data')),
            ass=json_serialize(data.get('ass')),
        )


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


class UiDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    base_data: UiBaseDataModel  # 基础信息
    test_case: UiTestCaseModel  # 测试用例信息
    data_clean: DataClean = DataClean()  # 缓存数据


class UiProjectDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    test_environment: EnvironmentEnum
    base_data: UiBaseDataModel
    test_data: ObtainTestData = ObtainTestData()
    cache_data: dict = {}
