# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏
from enums import BaseEnum
from enums.tools_enum import AutoTestTypeEnum


class ProjectEnum(BaseEnum):
    MOCK = '芒果mock'
    Gitee = 'gitee'
    SQL = 'sql'


auto_test_project_config = [
    {'type': AutoTestTypeEnum.API, 'project_name': ProjectEnum.MOCK, 'dir_name': 'api_mango_mock'},
    {'type': AutoTestTypeEnum.UI, 'project_name': ProjectEnum.Gitee, 'dir_name': 'ui_baidu'},
    {'type': AutoTestTypeEnum.OTHER, 'project_name': ProjectEnum.SQL, 'dir_name': 'sql_auto'},
]
