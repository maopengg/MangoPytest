# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 11:08
# @Author : 毛鹏
import os

import sys


class InitializationPath:
    current_directory = os.path.abspath(__file__)
    project_root_directory = os.path.dirname(os.path.dirname(current_directory))
    current_dir2 = os.path.dirname(sys.executable)
    if 'python.exe' not in sys.executable:
        project_root_directory = current_dir2
    logs_dir = os.path.join(project_root_directory, "logs")
    cache_dir = os.path.join(project_root_directory, "cache")
    report_dir = os.path.join(project_root_directory, "report")
    reports_dir = os.path.join(project_root_directory, "reports")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    @classmethod
    def logs_path(cls):
        return cls.logs_dir

    @classmethod
    def directory_path(cls):
        return cls.project_root_directory

    @classmethod
    def cache_path(cls):
        return cls.cache_dir


if __name__ == '__main__':
    print(InitializationPath.logs_path())
    print(InitializationPath.directory_path())
    print(InitializationPath.cache_path())
