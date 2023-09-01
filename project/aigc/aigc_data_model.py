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
class AIGCDataModel(BaseModel):
    host: str
    headers: dict = {'Accept': 'application/json, text/plain, */*',
                     'Content-Type': 'application/json;charset=UTF-8',
                     'User': '',
                     'Authorization': '',
                     'userId': ''}
    # 'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    # 'Sec-Ch-Ua-Platform': '"Windows"'
    mysql_db: MysqlDBModel | None
    username: str = 'maopeng'
    password: str = '123456'
