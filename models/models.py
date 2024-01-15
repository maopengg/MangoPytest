from pydantic import BaseModel

from models.tools_model import MysqlConingModel
from tools.mysql_tool.mysql_control import MySQLHelper


def singleton(cls):
    instances = {}

    def _instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _instance


class CaseRunModel(BaseModel):
    project: str
    testing_environment: str


@singleton
class ProjectRunModel(BaseModel):
    list_run: list[CaseRunModel] | None


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


@singleton
class AigcSaasDataModel(BaseModel):
    host: str
    headers: dict = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*'
    }
    mysql_db: MysqlConingModel
    mysql_obj: MySQLHelper | None
    enterprise: str = 'yali005'
    username: str = 'test005@yali005.com'
    password: str = '123456'
    verification_code: str = 'AIgc2023aiGC'
    testing_environment: str
    db_is_ass: bool

    class Config:
        arbitrary_types_allowed = True
