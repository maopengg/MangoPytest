# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-01-17 11:11
# @Author : 毛鹏
import json

from mangotools.data_processor import DataClean
from pydantic import BaseModel, ConfigDict

from enums.ui_enum import BrowserTypeEnum


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


class UiDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    test_case: UiTestCaseModel  # 测试用例信息
    data_clean: DataClean = DataClean()  # 缓存数据
