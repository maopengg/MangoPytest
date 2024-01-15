# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-12-05 10:15
# @Author : 毛鹏
import json

import requests
import time

from enums.tools_enum import ProjectEnum
from exceptions.exception import LoginError
from models.models import ProjectRunModel, AigcSaasDataModel
from models.tools_model import MysqlConingModel
from project import TEST_PROJECT_MYSQL
from tools.logging_tool.log_control import INFO, ERROR
from tools.mysql_tool.mysql_control import MySQLHelper


def account():
    """
    企业账号yali001-->020
    账号test001-》020 @企业账号.com
    密码123456
    @return:
    """
    user = []
    for i in range(1, 21):
        if 0 <= i <= 9:
            enterprise = f'yali00{i}'
        else:
            enterprise = f'yali0{i}'
        for e in range(1, 21):
            if 0 <= e <= 9:
                username = f'test0{e}@{enterprise}.com'
            else:
                username = f'test00{e}@{enterprise}.com'
            user.append({"enterpriseName": enterprise, "userName": username, "password": 123456})
    return user


def aigc_saas_login():
    """
    登录接口
    :return:
    """
    project_run: ProjectRunModel = ProjectRunModel()
    testing_environment = None
    if project_run.list_run:
        testing_environment = next(
            (i.testing_environment for i in project_run.list_run if i.project == ProjectEnum.AIGCSAAS.value), None)

    if testing_environment is None:
        testing_environment = 'test'
        ERROR.logger.error(f'项目：{ProjectEnum.AIGCSAAS.value}未获取到测试环境变量，请检查！')
        time.sleep(5)
    sql = f'SELECT `host`,mysql_db,is_ass FROM aigc_AutoTestPlatform.project_config WHERE project_te = "{testing_environment}" AND project_name = "{ProjectEnum.AIGCSAAS.value}";'
    query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
    mysql_dict = json.loads(query['mysql_db'])
    mysql_db = MysqlConingModel(host=mysql_dict.get('host'),
                            port=mysql_dict.get('port'),
                            user=mysql_dict.get('user'),
                            password=mysql_dict.get('password'),
                            database=mysql_dict.get('database'))
    mysql_obj = MySQLHelper(mysql_db)
    data_model: AigcSaasDataModel = AigcSaasDataModel(host=query.get('host'),
                                                      mysql_db=json.loads(query.get('mysql_db')),
                                                      mysql_obj=mysql_obj,
                                                      testing_environment=testing_environment,
                                                      db_is_ass=True if query.get('is_ass') == 1 else False)

    url = f'{data_model.host}/dev-api/auth/oauth2/token'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Authorization': 'Basic eHVleWk6eHVleWk=',
    }

    test_case = {
        'enterpriseName': f'{data_model.enterprise}',
        'userName': f'{data_model.username}',
        'password': f'{data_model.password}',
        'code': f'{data_model.verification_code}',
        'uuid': '21cfcf8feaf84ed4a831c80662227d8c',
        'mode': 'none',
        'grant_type': 'password',
        'account_type': 'admin',
        'scope': 'server'
    }

    response = requests.post(url, headers=headers, data=test_case)
    try:
        token = response.json()['data']['access_token']
    except AttributeError:
        raise LoginError(f'登录接口异常，请先检查登录接口再进行自动化测试！登录接口响应结果：{response.json()}')
    data_model.headers['Authorization'] = 'Bearer ' + token
    INFO.logger.info(f'{ProjectEnum.CDXP.value}请求头设置成功！{data_model.headers}')


aigc_saas_login()
