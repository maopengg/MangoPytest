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
class CDXPDataModel(BaseModel):
    host: str
    headers: dict = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*'
    }
    mysql_db: MysqlConingModel
    mysql_obj: MySQLHelper | None
    username: str = 'maopeng@zalldigital.com'
    password: str = 'm729164035'
    testing_environment: str
    db_is_ass: bool

    class Config:
        arbitrary_types_allowed = True
