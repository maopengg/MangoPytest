# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2022-12-04 17:14
# @Author : 毛鹏
import json

from pydantic import BaseModel
from pydantic.v1 import ConfigDict

from models.tools_model import MysqlConingModel
from tools.database.mysql_connect import MySQLConnect


class TestCaseModel(BaseModel):
    id: int
    project_id: int
    name: str
    client_type: int
    method: int
    url: str
    params: dict | list[dict] | None = None
    data: dict | list[dict] | None = None
    json_data: dict | list[dict] | None = None
    file: dict | None = None
    other_data: dict | None = None
    ass_response_whole: str | None = None
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
            project_id=data['project_id'],
            name=data['name'],
            client_type=data['client_type'],
            method=data['method'],
            url=data['url'],
            params=json.loads(data.get('params')) if data.get('params') else None,
            data=json.loads(data.get('data')) if data.get('data') else None,
            json_data=json.loads(data.get('json_data')) if data.get('json_data') else None,
            file=json.loads(data.get('file')) if data.get('file') else None,
            other_data=json.loads(data.get('other_data')) if data.get('other_data') else None,
            ass_response_whole=data.get('ass_response_whole'),
            ass_response_value=data.get('ass_response_value'),
            ass_sql=data.get('ass_sql'),
            front_sql=data.get('front_sql'),
            posterior_sql=data.get('posterior_sql'),
            posterior_response=data.get('posterior_response'),
            dump_data=data.get('dump_data')
        )


class RequestModel(BaseModel):
    url: str
    method: str
    headers: dict
    params: dict | None = None
    data: str | dict | None = None
    json_data: dict | None = None
    file: dict | None = None


class ResponseModel(BaseModel):
    url: str
    status_code: int
    method: str
    headers: dict
    response_text: str
    response_dict: dict
    response_time: int | float | None = None


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


class ApiDataModel(BaseModel):
    base_data: ApiBaseDataModel
    test_case: TestCaseModel
    request: RequestModel | None = None
    response: ResponseModel | None = None
