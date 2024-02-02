# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏

from pydantic import BaseModel

from tools.database.mysql_control import MySQLHelper


class MysqlConingModel(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str | None


class DataModel(BaseModel):
    """
        每个自动化的项目要在这里设置全局通用的变量，如域名，测试环境，请求头等信息，后面在发生真正请求时，会使用这这里面的信息
    """
    test_object: dict  # 测试对象表
    project: dict  # 项目表
    user_info: dict  # 用户登录信息
    host: str  # 域名
    headers: dict  # 请求头
    is_database_assertion: bool
    mysql_model: MysqlConingModel | None
    mysql_client_obj: MySQLHelper | None
    other_data: dict | None  # 其他数据

    class Config:
        arbitrary_types_allowed = True


class CaseRunModel(BaseModel):
    project: str
    testing_environment: str


class TestMetrics(BaseModel):
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: str


class TestEnvironmentModel(BaseModel):
    host: str
    notification_type_list: list | None
    excel_report: bool
    database_assertion: bool
    mysql_db: MysqlConingModel


class TestReportModel(BaseModel):
    test_suite_id: int
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
