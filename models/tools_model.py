# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏

from pydantic import BaseModel


class MysqlConingModel(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str | None


class CaseRunModel(BaseModel):
    project: str
    type: int
    test_environment: str


class TestMetrics(BaseModel):
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: str


class TestReportModel(BaseModel):
    project_id: str
    project_name: str
    test_environment: str
    case_sum: int
    success: int
    success_rate: float
    warning: int
    fail: int
    execution_duration: int
    test_time: str
    ip: str


class WeChatNoticeModel(BaseModel):
    webhook: str


class EmailNoticeModel(BaseModel):
    send_list: list
