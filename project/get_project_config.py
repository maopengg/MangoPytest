# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2023-09-17 22:50
# @Author : 毛鹏
from typing import Union

from enums.tools_enum import ProjectEnum
from models.models import AIGCDataModel, CDXPDataModel, AigcSaasDataModel


def get_project_config(project: str) -> Union[AIGCDataModel, CDXPDataModel, AigcSaasDataModel]:
    """
    根据项目名称，获取对应的项目配置模型
    @param project:
    @return:
    """
    if project == ProjectEnum.AIGC.value:
        return AIGCDataModel()
    elif project == ProjectEnum.CDXP.value:
        return CDXPDataModel()
    elif project == ProjectEnum.AIGCSAAS.value:
        return AigcSaasDataModel()


if __name__ == '__main__':
    get_project_config('cdxp')
