# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏

from enums import BaseEnum
from tools import InitPath


class ProjectEnum(BaseEnum):
    CDP = 'CDP'
    WanAndroid = 'WanAndroid'
    BaiduTranslate = 'BaiduTranslate'
    Gitee = 'Gitee'
    Mango = 'MangoTestingPlatform'


class CDPEnum(BaseEnum):
    NAME = ProjectEnum.CDP.value
    UI_PATH = fr"{InitPath.project_root_directory}\auto_test\ui\cdp\test_case"
    API_PATH = fr"{InitPath.project_root_directory}\auto_test\api\cdp\test_case"


class WanAndroidEnum(BaseEnum):
    NAME = ProjectEnum.WanAndroid.value
    UI_PATH = fr"{InitPath.project_root_directory}\auto_test\ui\wan_android\test_case"
    API_PATH = fr"{InitPath.project_root_directory}\auto_test\api\wan_android\test_case"


class BaiduTranslateEnum(BaseEnum):
    NAME = ProjectEnum.BaiduTranslate.value
    API_PATH = fr"{InitPath.project_root_directory}\auto_test\api\baidu_translate\test_case"


class GiteeEnum(BaseEnum):
    NAME = ProjectEnum.Gitee.value
    UI_PATH = fr"{InitPath.project_root_directory}\auto_test\ui\gitee\test_case"


class MangoTestingPlatformEnum(BaseEnum):
    NAME = ProjectEnum.Mango.value
    API_PATH = fr"{InitPath.project_root_directory}\auto_test\api\mango_testing_platform\test_case"