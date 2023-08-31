# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 15:09
# @Author : 毛鹏
from pydantic import BaseModel

from models.tools_model import MysqlDBModel


def singleton(cls):
    instances = {}

    def _instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _instance


@singleton
class CDXPDataModel(BaseModel):
    host: str
    headers: dict = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*'}
    mysql_db: MysqlDBModel | None
    username: str = 'maopeng@zalldigital.com'
    password: str = 'maopeng123'
