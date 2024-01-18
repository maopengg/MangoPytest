# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏


from pydantic import BaseModel

from tools.database.mysql_control import MySQLHelper
from tools.decorator.singleton import singleton


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


@singleton
class ProjectRunModel(BaseModel):
    list_run: list[CaseRunModel] | None


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


class EmailModel(BaseModel):
    send_user: str
    email_host: str
    # 自己到QQ邮箱中配置stamp_key
    stamp_key: str
    # 收件人改成自己的邮箱
    send_list: list

    @classmethod
    def get_obj(cls, data: dict):
        return cls(send_user=data.get('send_user'),
                   email_host=data.get('email_host'),
                   stamp_key=data.get('stamp_key'),
                   send_list=eval(data.get('send_list')))


class WeChatSendModel(BaseModel):
    metrics: TestMetrics
    environment: str
    project: str
    webhook: str


class EmailSendModel(BaseModel):
    metrics: TestMetrics
    environment: str
    project: str
    config: EmailModel
