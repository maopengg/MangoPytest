# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-20 10:56
# @Author : 毛鹏

from auto_test.project_config import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum
from models.ui_model import UiProjectDataModel
from tools.log import log
from tools.project_public_methods import ProjectPublicMethods


def data_init():
    """
    项目数据初始化
    :return:
    """
    data_model: UiProjectDataModel = ProjectPublicMethods.get_data_model(
        UiProjectDataModel,
        ProjectEnum.WanAndroid.value,
        AutoTestTypeEnum.UI
    )

    log.info(f'{ProjectEnum.WanAndroid.value}的UI在自动化基础信息设置完成！')
    return data_model


ui_project_data_model = data_init()
