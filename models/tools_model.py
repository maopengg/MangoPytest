# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏

from pydantic import BaseModel

from auto_test.project_config import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum


class CaseRunModel(BaseModel):
    project: ProjectEnum
    type: AutoTestTypeEnum
    test_environment: EnvironmentEnum


class CaseRunListModel(BaseModel):
    case_run: list[CaseRunModel]


class TestMetrics(BaseModel):
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: float


class SheetModel(BaseModel):
    id: str
    title: str


class SurfaceConfigModel(BaseModel):
    id: str
    sheet: list[SheetModel]


class SurfaceModel(BaseModel):
    api_info: SurfaceConfigModel
    api_test_case: SurfaceConfigModel
    project: SurfaceConfigModel
    ui_element: SurfaceConfigModel
    ui_test_case: SurfaceConfigModel
    other_test_case: SurfaceConfigModel


class FeiShuModel(BaseModel):
    app_id: str
    app_secret: str
    surface: SurfaceModel
