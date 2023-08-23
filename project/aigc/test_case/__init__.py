# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 10:57
# @Author : 毛鹏
import requests
from requests import Response

from enums.tools_enum import ProjectEnum
from project.aigc import AIGCDataModel
from project.aigc.modules.login.login import LoginAPI
from tools.data_processor import DataProcessor
from tools.logging_tool.log_control import ERROR

project = ProjectEnum.AIGC.value

data_model: AIGCDataModel = AIGCDataModel()


def api_login() -> Response:
    """
    登录接口
    :return:
    """
    password = DataProcessor.md5_encrypt(data_model.password)
    url = data_model.host + f'api/login'
    json = {"username": data_model.username, "password": password}
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
    }
    return requests.post(url=url, headers=headers, json=json)


try:
    response: Response = api_login()
    token = response.json().get('data').get('token')
    data_model.headers['Authorization'] = 'Bearer ' + token
    data_model.headers['User'] = data_model.username
    data_model.headers['userId'] = "11"
except Exception as e:
    ERROR.logger.error(f"设置{project}的token失败，请重新设置:{e}")
