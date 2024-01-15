#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2023/08/07 11:01
# @Author :
import os

import pytest

from config.settings import *
from enums.tools_enum import ProjectEnum
from models.models import ProjectRunModel, CaseRunModel
from project import notify_send
from tools.files.zip_files import zip_files
from tools.logging_tool.log_control import INFO
from tools.read_files_tools.get_local_ip import get_host_ip


class Run:

    def __init__(self, data: list[dict]):
        self.data: ProjectRunModel = ProjectRunModel(list_run=[CaseRunModel(**i) for i in data])
        self.pytest_command = ['-s', '-W', 'ignore:Module already imported:pytest.PytestWarning',
                               '--alluredir', './report/tmp', "--clean-alluredir", ]
        """
            --reruns: 失败重跑次数
            --count: 重复执行次数
            -v: 显示错误位置以及错误的详细信息
            -s: 等价于 pytest --capture=no 可以捕获print函数的输出
            -q: 简化输出信息
            -m: 运行指定标签的测试用例
            -x: 一旦错误，则停止运行
            --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
            "--reruns=3", "--reruns-delay=2"
            -n 4: 代表使用多线程执行用例，4是线程数
        """
        # 压缩上一次执行结果，并且保存起来，方便后面查询
        zip_files()
        self.run()

    def run(self):
        # 循环准备开始执行用例
        for project_obj in self.data.list_run:
            if project_obj.project == ProjectEnum.AIGC.value:
                self.pytest_command.append(AIGC_PATH)
            elif project_obj.project == ProjectEnum.CDXP.value:
                self.pytest_command.append(CDXP_PATH)
            elif project_obj.project == ProjectEnum.AIGCSAAS.value:
                self.pytest_command.append(AIGC_SAAS_PATH)
        # 执行用例
        INFO.logger.info(f"开始执行测试任务...")
        pytest.main(self.pytest_command)
        os.system(r"allure generate ./report/tmp -o ./report/html --clean")
        # 发送通知
        notify_send(self.data)
        # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
        os.system(f"allure serve ./report/tmp -h {get_host_ip()} -p 9998")


if __name__ == '__main__':
    # Run([{'project': 'aigc', 'testing_environment': 'test'}])
    # Run([{'project': 'cdxp', 'testing_environment': 'pre'}])
    # Run([{'project': 'aigc', 'testing_environment': 'test'}])
    Run([{'project': 'aigc-saas', 'testing_environment': 'test'},{'project': 'aigc', 'testing_environment': 'test'},{'project': 'cdxp', 'testing_environment': 'pre'}])
