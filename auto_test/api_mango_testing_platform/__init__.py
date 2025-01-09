from urllib.parse import urljoin

from mangokit import singleton, requests
from pydantic import BaseModel, ConfigDict

from auto_test.project_config import ProjectEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from models.api_model import ApiBaseDataModel
from tools.log import log
from tools.obtain_test_data import ObtainTestData
from tools.project_public_methods import ProjectPublicMethods


@singleton
class MangoDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_info: dict = {"username": "17798339533", "password": "1234567"}
    headers: dict = {}

    test_environment: EnvironmentEnum
    base_data: ApiBaseDataModel
    test_data: ObtainTestData = ObtainTestData()
    cache_data: dict = {}


def data_init():
    """
    登录接口，获取通用token
    :return:
    """
    data_model: MangoDataModel = ProjectPublicMethods.get_data_model(
        MangoDataModel,
        ProjectEnum.Mango.value,
        AutoTestTypeEnum.API
    )
    login_url = f'login'
    try:
        response = requests.request(url=urljoin(data_model.base_data.test_object.get('host'), login_url),
                                    method="POST",
                                    headers=data_model.headers,
                                    data=data_model.user_info)
        data_model.headers['Authorization'] = response.json()['data']['token']
        data_model.base_data.headers = data_model.headers
        log.info(f'{ProjectEnum.Mango.value}的API在自动化基础信息设置完成！')
    except Exception as error:
        log.warning(f'{ProjectEnum.Mango.value}的服务未启动，请先启动服务再进行测试！')
        raise Exception(f'{ProjectEnum.Mango.value}的服务未启动，请先启动服务再进行测试！')


data_init()
