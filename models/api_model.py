# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2022-12-04 17:14
# @Author : 毛鹏

from typing import Union

from pydantic import BaseModel

from tools.data_processor import DataProcessor


class ApiInfoModel(BaseModel):
    id: int | None
    project: str
    name: str
    url: str
    type: int
    method: int
    headers: dict | None
    body: str | None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(id=data.get('id'),
                   project=data.get('project'),
                   name=data.get('name'),
                   url=data.get('url'),
                   type=data.get('type'),
                   method=data.get('method'),
                   api_id=data.get('api_id'),
                   headers=DataProcessor.json_loads(data.get('headers'))
                   )


class AssModel(BaseModel):
    actual: str
    ass_method: str
    expect: int | str | None


class AssListModel(BaseModel):
    ass_type: int
    sql: str | None = None
    expect_list: list[AssModel] | None


class AfterHandleListModel(BaseModel):
    after_handle: list[str]


class AfterHandleModel(BaseModel):
    type: int
    after_handle: list[AfterHandleListModel]

class TestCaseModel(BaseModel):
    id: int
    project: str
    modules: str
    api_name: str | None
    case_name: str
    case_step: list | None
    api_id: str
    case_params: dict | list[dict] | None
    case_data: str | dict | list[dict] | None
    case_json: dict | list[dict] | None
    case_ass: list[AssListModel | dict] | dict | None
    case_after: AfterHandleModel | None

    @classmethod
    def get_obj(cls, data: dict):
        return cls(id=data.get('id'),
                   project=data.get('project'),
                   modules=data.get('modules_api'),
                   api_name=data.get('api_name'),
                   case_name=data.get('case_name'),
                   case_step=eval(data.get('case_step')) if data.get('case_step') else None,
                   api_id=data.get('api_id'),
                   case_params=DataProcessor.json_loads(data.get('case_params')),
                   case_data=DataProcessor.json_loads(data.get('case_data')),
                   case_json=DataProcessor.json_loads(data.get('case_json')),
                   case_ass=DataProcessor.json_loads(data.get('case_ass')),
                   case_after=data.get('case_after')
                   )


class RequestDataModel(BaseModel):
    method: str | None
    method_list: list = ['GET', 'POST', 'DELETE', 'PUT']
    url: str | None
    headers: dict | None = None
    params: dict | None = None
    data: str | dict | None = None
    json_data: dict | None = None
    file: dict | None = None


class ResponseDataModel(BaseModel):
    url: str
    status_code: int
    method: str
    headers: dict
    body: str | dict | None
    encoding: str | None
    content: bytes | None
    text: str
    response_json: dict | str


class CaseGroupModel(BaseModel):
    api_id: int = None
    api_data: ApiInfoModel | None = None
    request: RequestDataModel = RequestDataModel()
    response: ResponseDataModel = None
    response_time: Union[int, float] = None


class ApiDataModel(BaseModel):
    project_id: int
    test_object_id: int
    case_id: int
    test_case_data: TestCaseModel
    db_is_ass: bool | None = None
    step: int = 0
    requests_list: list[CaseGroupModel] = [CaseGroupModel()]


if __name__ == '__main__':
    d = {'id': 10, 'project': 'aigc', 'modules_api': '用户退出', 'api_name': None, 'api_id': '2', 'case_name': '未登录，直接退出',
         'case_step': None, 'case_data': None, 'case_ass': '{"status": 1, "message": null, "data": null}'}

    TestCaseModel.get_obj(d)
