# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏
from enums import BaseEnum
from enums.tools_enum import AutoTestTypeEnum
from tools import InitializationPath
from tools.other_tools.path import Path


class ProjectEnum(BaseEnum):
    CDP = 'CDP'
    WanAndroid = 'WanAndroid'


class CDPEnum(BaseEnum):
    NAME = 'cdp'
    UI_PATH = Path.ensure_path_sep(fr"{InitializationPath.project_root_directory}\auto_test\ui\cdp\test_case")
    API_PATH = Path.ensure_path_sep(fr"{InitializationPath.project_root_directory}\auto_test\api\cdp\test_case")


class WanAndroidEnum(BaseEnum):
    NAME = 'WanAndroid'
    UI_PATH = Path.ensure_path_sep(fr"{InitializationPath.project_root_directory}\auto_test\ui\wan_android\test_case")
    API_PATH = Path.ensure_path_sep(fr"{InitializationPath.project_root_directory}\auto_test\api\wan_android\test_case")


project_type_paths = {
    CDPEnum.NAME.value: {
        AutoTestTypeEnum.UI.value: CDPEnum.UI_PATH.value,
        AutoTestTypeEnum.API.value: CDPEnum.API_PATH.value
    },
    WanAndroidEnum.NAME.value: {
        AutoTestTypeEnum.UI.value: WanAndroidEnum.UI_PATH.value,
        AutoTestTypeEnum.API.value: WanAndroidEnum.API_PATH.value
    }
}
