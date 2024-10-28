# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-28 15:19
# @Author : 毛鹏
from mangokit import DataProcessor, singleton
from pydantic import BaseModel, ConfigDict

from auto_test.project_config import GiteeEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from models.ui_model import UiBaseDataModel
from tools.log import log
from tools.project_public_methods import ProjectPublicMethods


@singleton
class GiteeDataModel(BaseModel):
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
    data_model: GiteeDataModel = ProjectPublicMethods.get_data_model(GiteeDataModel, GiteeEnum,
                                                                          AutoTestTypeEnum.UI)
    log.info(f'{GiteeEnum.NAME.value}的UI在自动化基础信息设置完成！')


data_init()
