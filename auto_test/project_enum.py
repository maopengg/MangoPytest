# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏

import functools
import multiprocessing
import threading

from enums import BaseEnum
from enums.tools_enum import AutoTestTypeEnum
from tools import InitializationPath


def singleton_lru_cache(maxsize=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, 'lock'):
                wrapper.lock = threading.Lock()
            if not hasattr(wrapper, 'cache'):
                wrapper.cache = {}
            key = (args, frozenset(kwargs.items()))
            with wrapper.lock:
                if key not in wrapper.cache:
                    wrapper.cache[key] = func(*args, **kwargs)
            return wrapper.cache[key]

        return wrapper

    return decorator


class ProjectEnum(BaseEnum):
    CDP = 'CDP'
    WanAndroid = 'WanAndroid'
    BaiduTranslate = 'BaiduTranslate'
    Gitee = 'Gitee'


class CDPEnum(BaseEnum):
    NAME = ProjectEnum.CDP.value
    UI_PATH = fr"{InitializationPath.project_root_directory}\auto_test\ui\cdp\test_case"
    API_PATH = fr"{InitializationPath.project_root_directory}\auto_test\api\cdp\test_case"


class WanAndroidEnum(BaseEnum):
    NAME = ProjectEnum.WanAndroid.value
    UI_PATH = fr"{InitializationPath.project_root_directory}\auto_test\ui\wan_android\test_case"
    API_PATH = fr"{InitializationPath.project_root_directory}\auto_test\api\wan_android\test_case"


class BaiduTranslateEnum(BaseEnum):
    NAME = ProjectEnum.BaiduTranslate.value
    API_PATH = fr"{InitializationPath.project_root_directory}\auto_test\api\baidu_translate\test_case"


class GiteeEnum(BaseEnum):
    NAME = ProjectEnum.Gitee.value
    UI_PATH = fr"{InitializationPath.project_root_directory}\auto_test\ui\gitee\test_case"

def singleton(cls):
    instances = {}
    lock = threading.Lock()
    manager = multiprocessing.Manager()

    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
@singleton

class ProjectTypePaths:

    def __init__(self):
        self.data = {
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
            }
        }

    def set_test_environment(self, project_name: ProjectEnum, value):
        self.data[project_name]['test_environment'] = value
