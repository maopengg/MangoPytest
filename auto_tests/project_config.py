# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏
from core.enums import BaseEnum
from core.enums.tools_enum import AutoTestTypeEnum


# 名称要和项目表的名称保持一致
class ProjectEnum(BaseEnum):
    MOCK_API = 'MockAPI服务'
    MOCK_UI = 'MockUI服务'
    BAIDU = '百度'
    SQL = 'sql'
    DEMO_PROJECT = 'demo_project'


auto_test_project_config = [
    {'type': AutoTestTypeEnum.API, 'project_name': ProjectEnum.MOCK_API, 'dir_name': 'api_mango_mock'},
    {'type': AutoTestTypeEnum.API, 'project_name': ProjectEnum.DEMO_PROJECT, 'dir_name': 'demo_project'},
    {'type': AutoTestTypeEnum.UI, 'project_name': ProjectEnum.MOCK_UI, 'dir_name': 'ui_mango_mock'},
    {'type': AutoTestTypeEnum.UI, 'project_name': ProjectEnum.BAIDU, 'dir_name': 'ui_baidu'},
    {'type': AutoTestTypeEnum.OTHER, 'project_name': ProjectEnum.SQL, 'dir_name': 'sql_auto'},
]
