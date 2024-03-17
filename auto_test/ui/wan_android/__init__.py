# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-02-20 10:56
# @Author : 毛鹏
# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2024-02-20 10:56
# @Author : 毛鹏
from pydantic import BaseModel
from pydantic.v1 import ConfigDict

from auto_test import UiBaseDataModel
from auto_test.project_enum import WanAndroidEnum
from enums.tools_enum import EnvironmentEnum
from tools.data_processor import DataProcessor
from tools.decorator.singleton import singleton
from tools.logging_tool.log_control import INFO
from tools.other_tools.project_public_methods import ProjectPublicMethods


@singleton
class WanAndroidDataModel(BaseModel):
    test_environment: EnvironmentEnum
    base_data_model: UiBaseDataModel
    data_processor: DataProcessor = DataProcessor()
    cache_data: dict | None = None

    class Config(ConfigDict):
        arbitrary_types_allowed = True


def data_initial():
    """
    项目数据初始化
    :return:
    """
    test_environment, project, test_object = ProjectPublicMethods.get_project_test_object(
        project_name=WanAndroidEnum.NAME.value,
        test_environment=EnvironmentEnum.PRO)
    mysql_config_model, mysql_connect = ProjectPublicMethods.get_mysql_info(test_object)
    WanAndroidDataModel(
        test_environment=test_environment,
        base_data_model=UiBaseDataModel(
            test_object=test_object,
            project=project,
            host=test_object.get('host'),
            is_database_assertion=bool(test_object.get('is_db')),
            mysql_config_model=mysql_config_model,
            mysql_connect=mysql_connect,
        )
    )
    INFO.logger.info(f'{WanAndroidEnum.NAME.value}的UI在自动化基础信息设置完成！')


data_initial()
