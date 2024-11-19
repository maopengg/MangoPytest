from urllib.parse import urljoin

from mangokit import singleton, requests
from pydantic import BaseModel, ConfigDict
from tools.obtain_test_data import ObtainTestData
from auto_test.project_config import WanAndroidEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from models.api_model import ApiBaseDataModel
from tools.log import log
from tools.project_public_methods import ProjectPublicMethods


@singleton
class WanAndroidDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_info: dict = {"username": "maopeng", "password": "729164035"}
    headers: dict = {'Content-Type': 'application/x-www-form-urlencoded'}

    test_environment: EnvironmentEnum
    base_data_model: ApiBaseDataModel
    test_data: ObtainTestData = ObtainTestData()
    cache_data: dict = {}


def data_init():
    """
    登录接口，获取通用token
    :return:
    """
    data_model: WanAndroidDataModel = ProjectPublicMethods.get_data_model(WanAndroidDataModel, WanAndroidEnum,
                                                                          AutoTestTypeEnum.API)
    login_url = f'user/login'
    response = requests.request(url=urljoin(data_model.base_data_model.test_object.get('host'), login_url),
                                method="POST",
                                headers=data_model.headers,
                                data=data_model.user_info)
    cookies = ''
    for k, v in response.cookies.items():
        _cookie = k + "=" + v + ";"
        # 拿到登录的cookie内容，cookie拿到的是字典类型，转换成对应的格式
        cookies += _cookie
        # 将登录接口中的cookie写入缓存中，其中login_cookie是缓存名称
    data_model.headers['cookie'] = cookies
    data_model.base_data_model.headers = data_model.headers
    log.info(f'{WanAndroidEnum.NAME.value}的API在自动化基础信息设置完成！')


data_init()
