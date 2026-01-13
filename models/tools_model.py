# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏
from mangotools.database import MysqlConnect
from mangotools.models import MysqlConingModel
from pydantic import BaseModel, ConfigDict

from auto_test.project_config import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum
from tools.obtain_test_data import ObtainTestData


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
    api_info_id: str
    api_test_case_id: str
    project: SurfaceConfigModel
    ui_element_id: str
    ui_test_case_id: str
    other_test_case_id: str


class FeiShuModel(BaseModel):
    app_id: str
    app_secret: str
    surface: SurfaceModel


class ProjectModel(BaseModel):
    id: int
    name: str


class TestObjectModel(BaseModel):
    id: int
    project_name: str
    type: int
    client_type: int
    host: str
    is_use: int
    is_notice: int
    db_c_status: int = 0
    db_rud_status: int = 0
    db_host: str | None = None
    db_port: int | None = None
    db_user: str | None = None
    db_password: str | None = None
    db_database: str | None = None


class BaseDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    test_environment: EnvironmentEnum
    test_data: ObtainTestData = ObtainTestData()

    test_object: TestObjectModel
    project: ProjectModel
    mysql_config_model: MysqlConingModel | None = None
    mysql_connect: MysqlConnect | None = None
    headers: dict = {}

    cache_data: dict = {}
