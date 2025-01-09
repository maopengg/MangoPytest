# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏
import json

from mangokit import MysqlConingModel, MysqlConnect, DataClean
from pydantic import BaseModel, ConfigDict


def json_serialize(data: str | None):
    try:
        if isinstance(data, str):
            return json.loads(data)
        else:
            return data
    except (json.decoder.JSONDecodeError, TypeError):
        return data


class OtherBaseDataModel(BaseModel):
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


class OtherTestCaseModel(BaseModel):
    id: int
    project_name: str
    name: str
    data: dict | list[dict] | str | None = None
    other_data: dict | list[dict] | str | None = None
    ass_response_whole: dict | list[dict] | str | None = None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(
            id=data['id'],
            project_name=data['project_name'],
            name=data['name'],
            data=json_serialize(data.get('data')),
            other_data=json_serialize(data.get('other_data')),
            ass_response_whole=json_serialize(data.get('ass_response_whole')),
        )


class OtherDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    base_data: OtherBaseDataModel  # 基础信息
    test_case: OtherTestCaseModel  # 测试用例信息
    data_clean: DataClean = DataClean()  # 缓存数据
