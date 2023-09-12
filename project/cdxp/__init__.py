# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-12 17:41
# @Author : 毛鹏
import json

import requests

from enums.tools_enum import ProjectEnum
from exceptions.exception import TestEnvironmentNotObtainedError
from project import TEST_PROJECT_MYSQL
from project.cdxp.cdxp_data_model import CDXPDataModel
from tools.data_processor import DataProcessor
from tools.logging_tool.log_control import INFO


def cdxp_login():
    """
    登录接口
    :return:
    """
    q = DataProcessor.get_cache(f'{ProjectEnum.CDXP.value}_environment')
    q = 'pre'

    if q is None:
        raise TestEnvironmentNotObtainedError('未获取到测试环境变量，请检查！')
    sql = f'SELECT `host`,mysql_db FROM aigc_AutoTestPlatform.project_config WHERE project_te = "{q}" AND project_name = "{ProjectEnum.CDXP.value}";'
    query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
    data_model = CDXPDataModel(host=query.get('host'), mysql_db=json.loads(query.get('mysql_db')))

    password = DataProcessor.md5_encrypt(data_model.password)
    url = f'{data_model.host}/backend/api-auth/oauth/token?username={data_model.username}&password={password}&grant_type=password_code'
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }
    response = requests.post(url=url, headers=headers)
    token = response.json().get('data').get('access_token')
    data_model.headers['Authorization'] = 'Bearer ' + token
    data_model.headers['Currentproject'] = 'precheck'
    data_model.headers['Service'] = 'zall'
    data_model.headers['Userid'] = '201'
    INFO.logger.info(f'{ProjectEnum.CDXP.value}请求头设置成功！{data_model.headers}')


cdxp_login()
