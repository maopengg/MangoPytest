# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-12 17:41
# @Author : 毛鹏
import json

import requests

from auto_test.api_project.cdxp.sql import test_sql01
from auto_test.project_enum import ProjectEnum
from exceptions.api_exception import LoginError
from models.tools_model import MysqlConingModel, ProjectRunModel, DataModel
from tools.data_processor import DataProcessor
from tools.database.mysql_control import MySQLHelper
from tools.database.sqlite_handler import SQLiteHandler
from tools.logging_tool.log_control import INFO, WARNING




def cdp_login():
    """
    登录接口
    :return:
    """
    username = ''
    password = ''

    project_run: ProjectRunModel = ProjectRunModel()
    testing_environment = None
    if project_run.list_run:
        testing_environment = next(
            (i.testing_environment for i in project_run.list_run if i.project == ProjectEnum.CDP.value), None)

    if testing_environment is None:
        testing_environment = 'pre'
        WARNING.logger.warning(f'项目：{ProjectEnum.CDP.value}未获取到测试环境变量，请检查！')
    query: dict = SQLiteHandler().execute_sql(test_sql01)[0]
    mysql_dict = json.loads(query.get('mysql_db'))
    mysql_db = MysqlConingModel(host=mysql_dict.get('host'),
                                port=mysql_dict.get('port'),
                                user=mysql_dict.get('user'),
                                password=mysql_dict.get('password'),
                                database=mysql_dict.get('database'))
    mysql_obj = MySQLHelper(mysql_db)
    data_model = DataModel(host=query.get('host'),
                           mysql_db=json.loads(query.get('mysql_db')),
                           mysql_obj=mysql_obj,
                           testing_environment=testing_environment,
                           db_is_ass=True if query.get('is_ass') == 1 else False)

    password = DataProcessor().md5_encrypt(password)
    url = f'{data_model.host}/backend/api-auth/oauth/token?username={username}&password={password}&grant_type=password_code'
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }
    response = requests.post(url=url, headers=headers)
    try:
        token = response.json().get('data').get('access_token')
    except AttributeError:
        raise LoginError(f'登录接口异常，请先检查登录接口再进行自动化测试！登录接口响应结果：{response.json()}')
    data_model.headers['Authorization'] = 'Bearer ' + token
    data_model.headers['Currentproject'] = 'precheck'
    data_model.headers['Service'] = 'zall'
    data_model.headers['Userid'] = '201'
    INFO.logger.info(f'{ProjectEnum.CDP.value}请求头设置成功！{data_model.headers}')


cdp_login()
