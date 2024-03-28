from urllib.parse import urljoin

from pydantic import BaseModel
from pydantic.v1 import ConfigDict

from auto_test.project_enum import WanAndroidEnum
from enums.tools_enum import EnvironmentEnum
from models.api_model import ApiBaseDataModel
from tools.base_request.request_tool import RequestTool
from tools.data_processor import DataProcessor
from tools.decorator.singleton import singleton
from tools.logging_tool import logger
from tools.other_tools.project_public_methods import ProjectPublicMethods


@singleton
class WanAndroidDataModel(BaseModel):
    user_info: dict = {"username": "maopeng", "password": "729164035"}
    headers: dict = {'Content-Type': 'application/x-www-form-urlencoded'}

    test_environment: EnvironmentEnum
    base_data_model: ApiBaseDataModel
    data_processor: DataProcessor = DataProcessor()
    cache_data: dict | None = None

    class Config(ConfigDict):
        arbitrary_types_allowed = True


def data_initial():
    """
    登录接口，获取通用token
    :return:
    """
    test_environment, project, test_object = ProjectPublicMethods.get_project_test_object(
        project_name=WanAndroidEnum.NAME.value,
        test_environment=EnvironmentEnum.PRO)
    mysql_config_model, mysql_connect = ProjectPublicMethods.get_mysql_info(test_object)
    data_model: WanAndroidDataModel = WanAndroidDataModel(
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
    login_url = f'user/login'

    response = RequestTool.internal_http(url=urljoin(test_object.get('host'), login_url),
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
    logger.info(f'{WanAndroidEnum.NAME.value}的API在自动化基础信息设置完成！')


data_initial()
