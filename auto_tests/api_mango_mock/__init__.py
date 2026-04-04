from urllib.parse import urljoin

import requests

from auto_test.project_config import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum
from models.tools_model import BaseDataModel
from tools.log import log
from tools.project_public_methods import InitBaseData

user_info: dict = {"username": "testuser", "password": "482c811da5d5b4bc6d497ffa98491e38"}


def data_init():
    """
    登录接口，获取通用token
    """
    test_data: BaseDataModel = InitBaseData.main(
        ProjectEnum.MOCK_API.value,
        AutoTestTypeEnum.API
    )
    login_url = f'auth/login'
    print(urljoin(test_data.test_object.host, login_url))
    response = requests.request(url=urljoin(test_data.test_object.host, login_url),
                                method="POST",
                                json=user_info,
                                proxies={'http': None, 'https': None})
    print(response.text)
    test_data.headers['X-Token'] = response.json()['data']['token']
    test_data.headers['Content-Type'] = 'application/json'
    log.info(f'{ProjectEnum.MOCK_API.value}的API在自动化基础信息设置完成！')
    return test_data


base_data = data_init()
