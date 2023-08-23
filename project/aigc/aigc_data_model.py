# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 15:09
# @Author : 毛鹏
from pydantic import BaseModel

from enums.tools_enum import ProjectEnum
from models.tools_model import MysqlDBModel


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class AIGCDataModel(BaseModel):
    host: str
    headers: dict
    mysql_db: MysqlDBModel
    username: str = 'maopeng'
    password: str = '123456'
