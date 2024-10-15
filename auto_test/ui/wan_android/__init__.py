# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2024-02-20 10:56
# @Author : 毛鹏
from mangokit import DataProcessor, singleton
from pydantic import BaseModel, ConfigDict

from auto_test.project_enum import WanAndroidEnum
from enums.tools_enum import EnvironmentEnum
from models.ui_model import UiBaseDataModel
from tools.log_collector import log
from tools.other.project_public_methods import ProjectPublicMethods


@singleton
class WanAndroidDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    test_environment: EnvironmentEnum
    base_data_model: UiBaseDataModel
    data_processor: DataProcessor = DataProcessor()
    cache_data: dict = {}


def data_init():
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
    log.info(f'{WanAndroidEnum.NAME.value}的UI在自动化基础信息设置完成！')


data_init()
