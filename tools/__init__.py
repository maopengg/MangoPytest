# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-03-05 20:39
# @Author : 毛鹏
import os

import sys


class InitPath:
    current_directory = os.path.abspath(__file__)
    project_root_directory = os.path.dirname(os.path.dirname(current_directory))
    current_dir2 = os.path.dirname(sys.executable)
    if 'python.exe' not in sys.executable:
        project_root_directory = current_dir2
    logs_dir = os.path.join(project_root_directory, "logs")
    sqlite_dir = os.path.join(project_root_directory, r"sources\sql_data")
    report_dir = os.path.join(project_root_directory, "report")
    reports_dir = os.path.join(project_root_directory, "reports")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)


InitPath()
if __name__ == '__main__':
    print(InitPath.current_directory)
    print(InitPath.project_root_directory)
    print(InitPath.current_dir2)
    print(InitPath.logs_dir)
    print(InitPath.sqlite_dir)
    print(InitPath.reports_dir)
