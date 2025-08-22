# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-28 15:19
# @Author : 毛鹏

from auto_test.project_config import ProjectEnum
from enums.tools_enum import AutoTestTypeEnum
from models.tools_model import BaseDataModel
from tools.log import log
from tools.project_public_methods import InitBaseData


def data_init()->BaseDataModel:
    """
    项目数据初始化
    :return:
    """
    data_model: BaseDataModel = InitBaseData.main(
        ProjectEnum.Gitee.value,
        AutoTestTypeEnum.UI
    )

    log.info(f'{ProjectEnum.Gitee.value}的UI在自动化基础信息设置完成！')
    return data_model


base_data: BaseDataModel = data_init()
