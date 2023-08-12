# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-07 11:12
# @Author : 毛鹏

import requests
from requests.models import Response

from tools.logging_tool.log_control import INFO
from tools.data_processor import DataProcessor


def api_login(username, password):
    """
    登录接口
    :return:
    """
    password = DataProcessor.md5_encrypt(password)
    url = DataProcessor.cache_get(
        'host') + f'/backend/api-auth/oauth/token?username={username}&password={password}&grant_type=password_code'
    headers = {
        'Authorization': 'Basic d2ViQXBwOndlYkFwcA==',
        'Accept': 'application/json, text/plain, */*',
    }
    return requests.post(url=url, headers=headers)


response: Response = api_login("admin", "admin")
DataProcessor.cache_set('token', response.json().get('data').get('access_token'))
INFO.logger.info(f"token设置成功：{DataProcessor.cache_get('token')}")
