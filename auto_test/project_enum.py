# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏

import json

from enums import BaseEnum
from enums.tools_enum import AutoTestTypeEnum
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


class ProjectPaths:
    paths = fr"{InitPath.project_root_directory}\auto_test\data.json"

    @classmethod
    def init(cls):
        with open(cls.paths, 'w') as file:
            json.dump({
                CDPEnum.NAME.value: {
                    AutoTestTypeEnum.UI.value: CDPEnum.UI_PATH.value,
                    AutoTestTypeEnum.API.value: CDPEnum.API_PATH.value
                },
                WanAndroidEnum.NAME.value: {
                    AutoTestTypeEnum.UI.value: WanAndroidEnum.UI_PATH.value,
                    AutoTestTypeEnum.API.value: WanAndroidEnum.API_PATH.value
                },
                BaiduTranslateEnum.NAME.value: {
                    AutoTestTypeEnum.API.value: BaiduTranslateEnum.API_PATH.value
                },
                GiteeEnum.NAME.value: {
                    AutoTestTypeEnum.UI.value: GiteeEnum.UI_PATH.value
                },
                MangoTestingPlatformEnum.NAME.value: {
                    AutoTestTypeEnum.API.value: MangoTestingPlatformEnum.API_PATH.value
                }
            }, file)

    @classmethod
    def check(cls):
        with open(cls.paths, 'r') as file:
            return json.load(file)

    @classmethod
    def update(cls, project_name, value):
        with open(cls.paths, 'r') as file:
            data = json.load(file)
        data[project_name]['test_environment'] = value
        with open(fr"{InitPath.project_root_directory}\auto_test\data.json", 'w') as file:
            json.dump(data, file)
