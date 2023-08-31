# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-23 10:54
# @Author : 毛鹏
import requests
from requests import Response

from config.settings import AIGC_CONFING_PATH
from enums.tools_enum import ProjectEnum
from project.aigc.aigc_data_model import AIGCDataModel
from tools.data_processor import CacheTool
from tools.data_processor import DataProcessor
from tools.files.read_yml import YmlReader
from tools.logging_tool.log_control import ERROR, INFO

project = ProjectEnum.AIGC.value


def preparation():
    file = YmlReader(CacheTool.get_cache(f'{project}_environment'), AIGC_CONFING_PATH)
    environment = file.get_environment()
    AIGCDataModel(host=environment.host, mysql_db=environment.mysql_db)


try:
    # CacheTool.set_cache(f'{project}_environment', 'test')
    preparation()
except Exception as e:
    ERROR.logger.error(f'{project}缓存设置失败:{e}')


data_model: AIGCDataModel = AIGCDataModel()


def aigc_login() -> Response:
    """
    登录接口
    :return:
    """
    password = DataProcessor.md5_encrypt(data_model.password)
    url = f'{data_model.host}api/login'
    json = {"username": data_model.username, "password": password}
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
    }
    return requests.post(url=url, headers=headers, json=json)


try:
    response: Response = aigc_login()
    user_id = response.json().get('data').get('userId')
    token = response.json().get('data').get('token')
    data_model.headers['Authorization'] = 'Bearer ' + token
    data_model.headers['User'] = data_model.username
    data_model.headers['userId'] = str(user_id)
    INFO.logger.info(f'{project}请求头设置成功！{data_model.headers}')
except Exception as e:
    ERROR.logger.error(f"设置{project}的token失败，请重新设置:{e}")
