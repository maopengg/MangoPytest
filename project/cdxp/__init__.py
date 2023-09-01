# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-12 17:41
# @Author : 毛鹏
import requests
from requests.models import Response

from config.settings import CDXP_CONFING_PATH
from enums.tools_enum import ProjectEnum
from project.cdxp.cdxp_data_model import CDXPDataModel
from tools.data_processor import CacheTool
from tools.data_processor import DataProcessor
from tools.files.read_yml import YmlReader
from tools.logging_tool.log_control import ERROR, INFO

project = ProjectEnum.CDXP.value


def preparation():
    """
    读取配置文件，并放入模型类
    :return:
    """
    file = YmlReader(CacheTool.get_cache(f'{project}_environment'), CDXP_CONFING_PATH)
    environment = file.get_environment()
    CDXPDataModel(host=environment.host, mysql_db=environment.mysql_db)


try:
    CacheTool.set_cache(f'{project}_environment', 'test')
    preparation()
except Exception as e:
    ERROR.logger.error(f'{project}缓存设置失败:{e}')

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
