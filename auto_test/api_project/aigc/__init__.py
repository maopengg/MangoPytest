# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 10:54
# @Author : 毛鹏
import json

import requests

from auto_test.api_project import TEST_PROJECT_MYSQL
from auto_test.api_project.aigc_saas.data_model import AIGCDataModel
from auto_test.project_enum import ProjectEnum
from exceptions.api_exception import LoginError
from models.tools_model import MysqlConingModel, ProjectRunModel
from tools.data_processor import DataProcessor
from tools.database.mysql_control import MySQLHelper
from tools.logging_tool.log_control import INFO, WARNING


def aigc_login():
    """
    处理所有依赖关系
    :return:
    """
    # 获取项目的运行模块
    project_run: ProjectRunModel = ProjectRunModel()
    testing_environment = None
    if project_run.list_run:
        testing_environment = next(
            (i.testing_environment for i in project_run.list_run if i.project == ProjectEnum.AIGC.value), None)
    if testing_environment is None:
        testing_environment = 'test'
        WARNING.logger.warning(f'项目：{ProjectEnum.AIGC.value}未获取到测试环境变量，请检查！')
        # raise TestEnvironmentNotObtainedError('未获取到测试环境变量，请检查！')
    # 查询项目配置并设置到模型中缓存起来
    sql = f'SELECT `host`,mysql_db, is_ass FROM project_config WHERE project_te = "{testing_environment}" AND project_name = "{ProjectEnum.AIGC.value}";'
    query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
    mysql_dict = json.loads(query.get('mysql_db'))
    mysql_db = MysqlConingModel(host=mysql_dict.get('host'),
                                port=mysql_dict.get('port'),
                                user=mysql_dict.get('user'),
                                password=mysql_dict.get('password'),
                                database=mysql_dict.get('database'))
    mysql_obj = MySQLHelper(mysql_db)
    data_model = AIGCDataModel(host=query.get('host'),
                               mysql_db=mysql_db,
                               mysql_obj=mysql_obj,
                               testing_environment=testing_environment,
                               db_is_ass=True if query.get('is_ass') == 1 else False)
    url = f'{data_model.host}api/login'
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8'}
    # 登录账号A并设置headers
    response = requests.post(url=url,
                             headers=headers,
                             json={"username": data_model.username,
                                   "password": DataProcessor.md5_encrypt(data_model.password)})
    login_model = response.json()
    try:
        data_model.headers['Authorization'] = f'Bearer {login_model["data"]["token"]}'
        data_model.headers['User'] = login_model["data"]["userName"]
        data_model.headers['userId'] = str(login_model["data"]["userId"])
    except TypeError:
        raise LoginError(f'登录接口异常，请先检查登录接口再进行自动化测试！登录接口响应结果：{login_model}')
    # 登录账号B并设置headers
    response = requests.post(url=url,
                             headers=headers,
                             json={"username": data_model.username2,
                                   "password": DataProcessor.md5_encrypt(data_model.password2)})
    login_model = response.json()

    data_model.headers2['Authorization'] = f'Bearer {login_model["data"]["token"]}'
    data_model.headers2['User'] = login_model["data"]["userName"]
    data_model.headers2['userId'] = str(login_model["data"]["userId"])

    INFO.logger.info(f'{ProjectEnum.AIGC.value}请求头设置成功！{data_model.headers2}')

    # 设置部分内容到缓存中作为全局变量
    DataProcessor().set_cache('aigc_user_id', str(login_model["data"]["userId"]))


aigc_login()
