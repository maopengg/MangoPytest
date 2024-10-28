# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-20 10:56
# @Author : 毛鹏
from mangokit import DataProcessor, singleton
from pydantic import BaseModel, ConfigDict

from auto_test.project_config import WanAndroidEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from models.ui_model import UiBaseDataModel
from tools.log import log
from tools.project_public_methods import ProjectPublicMethods


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
    data_model: WanAndroidDataModel = ProjectPublicMethods.get_data_model(WanAndroidDataModel, WanAndroidEnum,
                                                                          AutoTestTypeEnum.UI)

    log.info(f'{WanAndroidEnum.NAME.value}的UI在自动化基础信息设置完成！')


data_init()
