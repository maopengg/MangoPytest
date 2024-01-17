# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2023-09-17 22:50
# @Author : 毛鹏
from auto_test.api_project.aigc.data_model import AigcSaasDataModel
from auto_test.api_project.aigc_saas.data_model import AIGCDataModel
from auto_test.api_project.cdxp.data_model import CDXPDataModel
from auto_test.project_enum import ProjectEnum


def get_project_config(project: str) -> AIGCDataModel or CDXPDataModel or AigcSaasDataModel:
    """
    根据项目名称，获取对应的项目配置模型
    @param project:
    @return:
    """
    if project == ProjectEnum.AIGC.value:
        return AIGCDataModel()
    elif project == ProjectEnum.CDP.value:
        return CDXPDataModel()
    elif project == ProjectEnum.AIGC_SAAS.value:
        return AigcSaasDataModel()


if __name__ == '__main__':
    get_project_config('cdp')
