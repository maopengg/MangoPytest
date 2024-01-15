# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 17:14
# @Author : 毛鹏

from dataclasses import dataclass
from typing import Text

from pydantic import BaseModel


@dataclass
class TestMetrics:
    """ 用例执行数据 """
    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text


class MysqlConingModel(BaseModel):
    host: str
    port: int
    user: str
    password: str
    database: str | None


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
                   send_list=eval(data.get('send_list')),
                   )


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
