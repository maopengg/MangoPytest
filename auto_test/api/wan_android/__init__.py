from urllib.parse import urljoin

from mangokit import singleton, requests
from pydantic import BaseModel, ConfigDict

from auto_test.project_config import WanAndroidEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from models.api_model import ApiBaseDataModel
from tools.log import log
from tools.obtain_test_data import ObtainTestData
from tools.project_public_methods import ProjectPublicMethods


@singleton
class WanAndroidDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_info: dict = {"username": "maopeng", "password": "729164035"}
    headers: dict = {'Content-Type': 'application/x-www-form-urlencoded'}

    test_environment: EnvironmentEnum
    base_data: ApiBaseDataModel
    test_data: ObtainTestData = ObtainTestData()
    cache_data: dict = {}


def data_init():
    """
    登录接口，获取通用token
    """
    data_model: WanAndroidDataModel = ProjectPublicMethods.get_data_model(WanAndroidDataModel, WanAndroidEnum,
                                                                          AutoTestTypeEnum.API)
    login_url = f'user/login'
    response = requests.request(url=urljoin(data_model.base_data.test_object.get('host'), login_url),
                                method="POST",
                                headers=data_model.headers,
                                data=data_model.user_info)
    cookies = ''
    for k, v in response.cookies.items():
        _cookie = k + "=" + v + ";"
        cookies += _cookie
    data_model.headers['cookie'] = cookies
    data_model.base_data.headers = data_model.headers
    log.info(f'{WanAndroidEnum.NAME.value}的API在自动化基础信息设置完成！')


data_init()
