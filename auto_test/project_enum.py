# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏
from enums import BaseEnum
from enums.tools_enum import AutoTestTypeEnum
from tools import InitializationPath
from tools.other_tools.path import Path


class CDPEnum(BaseEnum):
    CDP = 'cdp'
    UI_PATH = Path.ensure_path_sep(f"{InitializationPath.project_root_directory}/auto_test/ui/cdp/test_case")
    API_PATH = Path.ensure_path_sep("auto_test/api/cdp/test_case")


class AIGCEnum(BaseEnum):
    AIGC = 'aigc'
    UI_PATH = Path.ensure_path_sep("auto_test/ui/aigc/test_case")
    API_PATH = Path.ensure_path_sep("auto_test/api/aigc/test_case")


class AIGCSAASEnum(BaseEnum):
    AIGC_SAAS = 'aigc-saas'
    UI_PATH = Path.ensure_path_sep("auto_test/ui/aigc_saas/test_case")
    API_PATH = Path.ensure_path_sep("auto_test/api/aigc_saas/test_case")


project_type_paths = {
    CDPEnum.CDP.value: {
        AutoTestTypeEnum.UI.value: CDPEnum.UI_PATH.value,
        AutoTestTypeEnum.API.value: CDPEnum.API_PATH.value
    },
    AIGCEnum.AIGC.value: {
        AutoTestTypeEnum.UI.value: AIGCEnum.UI_PATH.value,
        AutoTestTypeEnum.API.value: AIGCEnum.API_PATH.value
    },
    AIGCSAASEnum.AIGC_SAAS.value: {
        AutoTestTypeEnum.UI.value: AIGCSAASEnum.UI_PATH.value,
        AutoTestTypeEnum.API.value: AIGCSAASEnum.API_PATH.value
    }
}
