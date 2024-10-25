from urllib.parse import urljoin

from mangokit import DataProcessor, singleton
from pydantic import BaseModel, ConfigDict

from auto_test.project_enum import MangoTestingPlatformEnum
from enums.tools_enum import EnvironmentEnum
from models.api_model import ApiBaseDataModel
from tools.base_request.request_tool import RequestTool
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
    test_environment, project, test_object = ProjectPublicMethods \
        .get_project_test_object(project_name=MangoTestingPlatformEnum.NAME.value,
                                 test_environment=EnvironmentEnum.TEST)
    mysql_config_model, mysql_connect = ProjectPublicMethods.get_mysql_info(test_object)
    data_model: MangoDataModel = MangoDataModel(
        test_environment=test_environment,
        base_data_model=ApiBaseDataModel(
            test_object=test_object,
            project=project,
            host=test_object.get('host'),
            is_database_assertion=bool(test_object.get('is_db')),
            mysql_config_model=mysql_config_model,
            mysql_connect=mysql_connect,
        )
    )
    login_url = f'login'
    try:
        response = RequestTool.internal_http(url=urljoin(test_object.get('host'), login_url),
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
