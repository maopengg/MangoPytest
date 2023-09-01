# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏

from pydantic import BaseModel

from models.models import TestMetrics


class MysqlDBModel(BaseModel):
    host: str
    port: int
    user: str
    password: str


class TestEnvironmentModel(BaseModel):
    host: str
    notification_type_list: list | None
    excel_report: bool
    database_assertion: bool
    mysql_db: MysqlDBModel


class EmailModel(BaseModel):
    send_user: str
    email_host: str
    # 自己到QQ邮箱中配置stamp_key
    stamp_key: str
    # 收件人改成自己的邮箱
    send_list: list


class WeChatSendModel(BaseModel):
    metrics: TestMetrics
    environment: str
    project: str
    webhook: str
    tester_name: str


class EmailSendModel(BaseModel):
    metrics: TestMetrics
    environment: str
    project: str
    config: EmailModel
