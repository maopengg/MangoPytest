# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏

from pydantic import BaseModel

from auto_test.project_enum import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum


class CaseRunModel(BaseModel):
    project: ProjectEnum
    type: AutoTestTypeEnum
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


class TestReportModel(BaseModel):
    project_id: str | int
    project_name: str
    test_environment: str
    case_sum: int
    success: int
    success_rate: float
    warning: int
    fail: int
    execution_duration: int | float
    test_time: str
    ip: str


class WeChatNoticeModel(BaseModel):
    webhook: str


class EmailNoticeModel(BaseModel):
    send_user: str
    email_host: str
    stamp_key: str
    send_list: list
