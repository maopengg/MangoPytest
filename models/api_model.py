# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2022-12-04 17:14
# @Author : 毛鹏
from pydantic import BaseModel


class ApiInfoModel(BaseModel):
    id: int | None
    name: str
    url: str
    type: int
    method: int
    headers: str | None
    body: dict | None


class TestCaseModel(BaseModel):
    id: int
    name: str
    api_id: str
    case_data: str | None
    case_ass: str | None


class ApiAndCaseInfo(BaseModel):
    caseName: str
    caseData: str
    apiName: str
    url: str
    caseAss: str | None
    type: int
    method: int
    headers: str | None


class listApiAndCaseInfo(BaseModel):
    case_list: list[ApiAndCaseInfo]
