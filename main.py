#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2023/08/07 11:01
# @Author : 毛鹏
import os

import pytest

from config.settings import AIGC_PATH, CDXP_PATH, CDXP_CONFING_PATH, AIGC_CONFING_PATH
from enums.tools_enum import NotificationType
from enums.tools_enum import ProjectEnum
from models.tools_model import EmailSendModel, WeChatSendModel
from tools.data_processor.cache_tool import CacheTool
from tools.files.read_yml import YmlReader
from tools.logging_tool.log_control import INFO
from tools.notify.send_mail import SendEmail
from tools.notify.wechat_send import WeChatSend
from tools.other_tools.allure_data.allure_report_data import AllureFileClean
from tools.other_tools.allure_data.error_case_excel import ErrorCaseExcel
from tools.read_files_tools.get_local_ip import get_host_ip


class Run:
    def __init__(self, data: dict):
        self.data = data
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
        """
        self.run()

    def run(self):
        project_str = ""
        for project, environment in self.data.items():
            if project == ProjectEnum.AIGC.value:
                self.pytest_command.append(AIGC_PATH)
                CacheTool.set_cache(f'{ProjectEnum.AIGC.value}_environment', environment)
                project_str += project + '+'
            elif project == ProjectEnum.CDXP.value:
                self.pytest_command.append(CDXP_PATH)
                CacheTool.set_cache(f'{ProjectEnum.CDXP.value}_environment', environment)
                project_str += project
        # 从配置文件中获取项目名称
        INFO.logger.info(f"开始执行{project_str}项目...")
        pytest.main(self.pytest_command)
        os.system(r"allure generate ./report/tmp -o ./report/html --clean")

        for project, environment in self.data.items():
            if project == ProjectEnum.AIGC.value:
                self.send(project, environment, AIGC_CONFING_PATH)
            elif project == ProjectEnum.CDXP.value:
                self.send(project, environment, CDXP_CONFING_PATH)

        # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
        os.system(f"allure serve ./report/tmp -h {get_host_ip()} -p 9999")

    def send(self, project, _environment, path):
        allure_data = AllureFileClean().get_case_count()

        reader = YmlReader(_environment, path)
        email = EmailSendModel(metrics=allure_data,
                               project=project,
                               environment=_environment,
                               config=reader.get_email())
        wechat = WeChatSendModel(metrics=allure_data,
                                 project=project,
                                 environment=_environment,
                                 webhook=reader.get_wechat(),
                                 tester_name=reader.get_tester_name())
        notification_mapping = {
            NotificationType.WECHAT.value: WeChatSend(wechat).send_wechat_notification,
            NotificationType.EMAIL.value: SendEmail(email).send_main}
        test_environment = reader.get_environment()
        for i in test_environment.notification_type_list:
            notification_mapping.get(i)()
        if test_environment.excel_report:
            ErrorCaseExcel().write_case()


if __name__ == '__main__':
    Run({'aigc': 'test', 'cdxp': 'pre'})
