# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 10:54
# @Author : 毛鹏
import json

import requests

from enums.tools_enum import ProjectEnum
from exceptions.exception import TestEnvironmentNotObtainedError
from project import TEST_PROJECT_MYSQL
from project.aigc.aigc_data_model import AIGCDataModel
from project.aigc.modules.login.model import ResponseModel
from tools.data_processor import DataProcessor
from tools.logging_tool.log_control import INFO


def aigc_login():
    """
    处理所有依赖关系
    :return:
    """
    q = DataProcessor.get_cache(f'{ProjectEnum.AIGC.value}_environment')
    # q = 'test'
    if q is None:
        raise TestEnvironmentNotObtainedError('未获取到测试环境变量，请检查！')
    sql = f'SELECT `host`,mysql_db FROM project_config WHERE project_te = "{q}" AND project_name = "{ProjectEnum.AIGC.value}";'
    query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
    data_model = AIGCDataModel(host=query.get('host'), mysql_db=json.loads(query.get('mysql_db')))

    password = DataProcessor.md5_encrypt(data_model.password)
    url = f'{data_model.host}api/login'
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8'}
    response = requests.post(url=url, headers=headers, json={"username": data_model.username, "password": password})
    login_model = ResponseModel.get_obj(response.json())

    data_model.headers['Authorization'] = f'Bearer {login_model.data.token}'
    data_model.headers['User'] = login_model.data.userName
    data_model.headers['userId'] = str(login_model.data.userId)

    INFO.logger.info(f'{ProjectEnum.AIGC.value}请求头设置成功！{data_model.headers}')


aigc_login()
