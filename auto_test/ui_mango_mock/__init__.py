# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-03 14:07
# @Author : 毛鹏

from auto_test.project_config import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum
from models.tools_model import BaseDataModel
from tools.log import log
from tools.project_public_methods import InitBaseData


def data_init() -> BaseDataModel:
    """
    项目数据初始化
    :return:
    """
    data_model: BaseDataModel = InitBaseData.main(
        ProjectEnum.MOCK_UI.value,
        AutoTestTypeEnum.UI
    )

    log.info(f'{ProjectEnum.MOCK_UI.value}的UI自动化基础信息设置完成！')
    return data_model


base_data_model: BaseDataModel = data_init()