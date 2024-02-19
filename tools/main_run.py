# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2024-02-19 10:07
# @Author : 毛鹏
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2023/08/07 11:01
# @Author :
import os

import pytest

from auto_test.project_enum import *
from models.tools_model import CaseRunModel
from tools.files.zip_files import zip_files
from tools.logging_tool.log_control import INFO
from tools.other_tools.native_ip import get_host_ip


class MainRun:

    def __init__(self, test_project: list[dict], pytest_command: list):
        self.data: list[CaseRunModel] = [CaseRunModel(**i) for i in test_project]
        self.pytest_command = pytest_command
        # 压缩上一次执行结果，并且保存起来，方便后面查询
        zip_files()
        self.run()

    def run(self):
        # 循环准备开始执行用例
        for case_run_model in self.data:
            if case_run_model.project in project_type_paths:
                project_paths = project_type_paths[case_run_model.project]
                project_paths['test_environment'] = case_run_model.test_environment
                if case_run_model.type in project_paths:
                    self.pytest_command.append(project_paths[case_run_model.type])
        # 执行用例
        INFO.logger.info(f"开始执行测试任务...")
        pytest.main(self.pytest_command)
        os.system(r"allure generate ./report/tmp -o ./report/html --clean")
        # 发送通知
        # notify_send(self.data)
        # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
        os.system(f"allure serve ./report/tmp -h {get_host_ip()} -p 9998")


if __name__ == '__main__':
    pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWarning', '--alluredir', './report/tmp',
                 '--clean-alluredir', 'D:\\GitCode\\PytestAutoTestauto_test\\ui\\cdp\\test_case'])
