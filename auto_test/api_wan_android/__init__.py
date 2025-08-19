from urllib.parse import urljoin

import requests

from auto_test.project_config import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum
from models.tools_model import BaseDataModel
from tools.log import log
from tools.project_public_methods import ProjectPublicMethods

user_info: dict = {"username": "maopeng", "password": "729164035"}


def data_init():
    """
    登录接口，获取通用token
    """
    test_data: BaseDataModel = ProjectPublicMethods.get_data_model(
        ProjectEnum.WanAndroid.value,
        AutoTestTypeEnum.API
    )
    login_url = f'user/login'
    response = requests.request(url=urljoin(test_data.test_object.host, login_url),
                                method="POST",
                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                data=user_info,
                                proxies={'http': None, 'https': None})
    cookies = ''
    for k, v in response.cookies.items():
        _cookie = k + "=" + v + ";"
        cookies += _cookie
    test_data.headers['cookie'] = cookies
    log.info(f'{ProjectEnum.WanAndroid.value}的API在自动化基础信息设置完成！')
    return test_data


base_data = data_init()
