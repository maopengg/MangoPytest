# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2022-12-04 17:14
# @Author : 毛鹏
import json

from mangotools.data_processor import DataClean
from mangotools.database import MysqlConnect
from mangotools.models import MysqlConingModel

from pydantic import BaseModel, ConfigDict

from exceptions import *


def json_serialize(data: str | None):
    try:
        if isinstance(data, str):
            return json.loads(data)
        else:
            return data
    except (json.decoder.JSONDecodeError, TypeError):
        raise ToolsError(*ERROR_MSG_0345, value=(data,))


class ApiTestCaseModel(BaseModel):
    id: int
    project_name: str
    name: str
    params: dict | list[dict] | list | None = None
    data: dict | list[dict] | list | None = None
    json_data: dict | list[dict] | list | None = None
    file: list[dict] | None = None
    other_data: dict | None = None
    ass_response_whole: dict | None = None
    ass_response_value: str | None = None
    ass_sql: str | None = None
    front_sql: str | None = None
    posterior_sql: str | None = None
    posterior_response: str | None = None
    dump_data: str | None = None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(
            id=data['id'],
            project_name=data['project_name'],
            name=data['name'],
            params=json_serialize(data.get('params')),
            data=json_serialize(data.get('data')),
            json_data=json_serialize(data.get('json')),
            file=json_serialize(data.get('file')),
            other_data=json_serialize(data.get('other_data')),
            ass_response_whole=json_serialize(data.get('ass_response_whole')),
            ass_response_value=data.get('ass_response_value'),
            ass_sql=data.get('ass_sql'),
            front_sql=data.get('front_sql'),
            posterior_sql=data.get('posterior_sql'),
            posterior_response=data.get('posterior_response'),
            dump_data=data.get('dump_data')
        )


class ApiInfoModel(BaseModel):
    id: int
    project_name: str
    name: str
    client_type: int
    method: int
    url: str
    json_data: dict | list | None = None
    headers: dict | None = None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(
            id=data['id'],
            project_name=data['project_name'],
            name=data['name'],
            client_type=data['client_type'],
            method=data['method'],
            url=data['url'],
            headers=json_serialize(data.get('headers')),
            json_data=json_serialize(data.get('JSON')),
        )


class RequestModel(BaseModel):
    url: str
    method: str
    headers: dict | None = None
    params: dict | None = None
    data: str | dict | None = None
    json_data: dict | list | None = None
    file: list | None = None


class ResponseModel(BaseModel):
    url: str
    status_code: int
    method: str
    headers: dict
    response_text: str
    response_dict: dict | list | None = None
    response_time: int | float | None = None
    content: bytes | None = None


class ApiBaseDataModel(BaseModel):
    """
        每个自动化的项目要在这里设置全局通用的变量，如域名，测试环境，请求头等信息，后面在发生真正请求时，会使用这这里面的信息
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    test_object: dict  # 测试对象表
    project: dict  # 项目表
    host: str  # 域名
    headers: dict | None = None  # 请求头
    is_database_assertion: bool
    mysql_config_model: MysqlConingModel | None = None
    mysql_connect: MysqlConnect | None = None


class ApiDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_data: ApiBaseDataModel  # 基础信息
    test_case: ApiTestCaseModel  # 测试用例信息
    data_clean: DataClean = DataClean()  # 缓存数据
    request: RequestModel | None = None
    response: ResponseModel | None = None
    other_data: dict = {}  # 其他数据
