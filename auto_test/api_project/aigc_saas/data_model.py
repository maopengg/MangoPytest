# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 14:43
# @Author : 毛鹏
from pydantic import BaseModel

from models.tools_model import MysqlConingModel
from tools.database.mysql_control import MySQLHelper
from tools.decorator.singleton import singleton


@singleton
class AIGCDataModel(BaseModel):
    host: str
    headers: dict = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    headers2: dict = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    username: str = 'auto_aigc'
    password: str = '123456'
    username2: str = 'maopeng'
    password2: str = '123456'
    mysql_db: MysqlConingModel
    mysql_obj: MySQLHelper | None
    testing_environment: str
    db_is_ass: bool

    class Config:
        arbitrary_types_allowed = True
