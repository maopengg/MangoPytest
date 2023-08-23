# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 10:57
# @Author : 毛鹏
import requests
from requests import Response

from enums.tools_enum import ProjectEnum
from tools.data_processor import DataProcessor
from tools.logging_tool.log_control import ERROR, INFO

project = ProjectEnum.AIGC.value


def api_login(username, password) -> Response:
    """
    登录接口
    :return:
    """
    password = DataProcessor.md5_encrypt(password)
    url = DataProcessor.cache_get(f'{project}_host') + f'api/login'
    json = {"username": username, "password": password}
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
    }
    return requests.post(url=url, headers=headers, json=json)


try:
    response: Response = api_login("maopeng", "123456")
    DataProcessor.cache_set(f'{project}_token', response.json().get('data').get('token'))
    INFO.logger.info(f"{project}token设置成功：{DataProcessor.cache_get(f'{project}_token')}")
except Exception as e:
    ERROR.logger.error(f"设置{project}的token失败，请重新设置:{e}")
