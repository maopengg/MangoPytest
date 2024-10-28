from urllib.parse import urljoin

from mangokit import DataProcessor, singleton, requests
from pydantic import BaseModel, ConfigDict

from auto_test.project_config import MangoTestingPlatformEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from models.api_model import ApiBaseDataModel
from tools.log import log
from tools.project_public_methods import ProjectPublicMethods


@singleton
class MangoDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_info: dict = {"username": "17798339533", "password": "1234567"}
    headers: dict = {}

    test_environment: EnvironmentEnum
    base_data_model: ApiBaseDataModel
    data_processor: DataProcessor = DataProcessor()
    cache_data: dict = {}


def data_init():
    """
    登录接口，获取通用token
    :return:
    """
    data_model: MangoDataModel = ProjectPublicMethods.get_data_model(MangoDataModel, MangoTestingPlatformEnum,
                                                                          AutoTestTypeEnum.API)
    login_url = f'login'
    try:
        response = requests.request(url=urljoin(data_model.base_data_model.test_object.get('host'), login_url),
                                    method="POST",
                                    headers=data_model.headers,
                                    data=data_model.user_info)
        data_model.headers['Authorization'] = response.json()['data']['token']
        data_model.base_data_model.headers = data_model.headers
        log.info(f'{MangoTestingPlatformEnum.NAME.value}的API在自动化基础信息设置完成！')
    except Exception as error:
        log.warning(f'{MangoTestingPlatformEnum.NAME.value}的服务未启动，请先启动服务再进行测试！')
        raise Exception(f'{MangoTestingPlatformEnum.NAME.value}的服务未启动，请先启动服务再进行测试！')


data_init()
