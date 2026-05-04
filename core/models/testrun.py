# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 测试运行相关数据模型
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏
import warnings

from pydantic import BaseModel

from core.enums.tools_enum import EnvironmentEnum

warnings.filterwarnings(
    "ignore",
    message='Field name "json"'
)


class CaseRunModel(BaseModel):
    project: str
    test_environment: EnvironmentEnum


class TestMetrics(BaseModel):
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: float


class SurfaceModel(BaseModel):
    ui_element_id: str


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
