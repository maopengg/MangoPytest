# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏
import json

from auto_test.project_config import *
from enums.tools_enum import AutoTestTypeEnum


class ProjectPaths:
    paths = fr"{InitPath.project_root_directory}\tools\project_path\data.json"

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
