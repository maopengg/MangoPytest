# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-07 11:12
# @Author : 毛鹏

import requests
from requests.models import Response

from enums.tools_enum import ProjectEnum
from project.cdxp import CDXPDataModel
from tools.data_processor import DataProcessor
from tools.logging_tool.log_control import ERROR, INFO

project = ProjectEnum.CDXP.value
data_model: CDXPDataModel = CDXPDataModel()


def cdxp_login(username, password) -> Response:
    """
    登录接口
    :return:
    """
    password = DataProcessor.md5_encrypt(password)
    url = f'{data_model.host}/backend/api-auth/oauth/token?username={username}&password={password}&grant_type=password_code'
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }
    return requests.post(url=url, headers=headers)


try:
    response: Response = cdxp_login("admin", "admin")
    token = response.json().get('data').get('access_token')
    data_model.headers['Authorization'] = 'Bearer ' + token
    data_model.headers['Currentproject'] = 'precheck'
    data_model.headers['Service'] = 'zall'
    data_model.headers['Userid'] = '201'
    INFO.logger.info(f'{project}请求头设置成功！{data_model.headers}')
except Exception as e:
    ERROR.logger.error(f"设置{project}的token失败，请重新设置{e}")
