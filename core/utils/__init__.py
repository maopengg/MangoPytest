# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core Utils - 通用工具
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core Utils 模块

提供通用的工具函数和装饰器
"""

from .helpers import generate_id, merge_dicts, filter_dict
from .log import log
from .obtain_test_data import ObtainTestData
from .project_dir import ProjectDir
from .project_public_methods import InitBaseData
from .zip_files import zip_files

project_dir = ProjectDir()

__all__ = [
    # 辅助函数
    "generate_id",
    "merge_dicts",
    "filter_dict",
    "log",
    "ObtainTestData",
    "InitBaseData",
    "zip_files",
    "project_dir",
]

if __name__ == '__main__':
    print(project_dir.root_path())
    print(project_dir.download())
    print(project_dir.logs())
    print(project_dir.reports())
    print(project_dir.report())
