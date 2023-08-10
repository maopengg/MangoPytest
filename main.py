#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2023/08/07 11:01
# @Author : 毛鹏
import os

import pytest

from models.models import NotificationType
from tools.files.read_yml import YAMLReader
from tools.logging_tool.log_control import INFO
from tools.mysql_tool.mysql_control import MySQLHelper
from tools.notify.send_mail import SendEmail
from tools.notify.wechat_send import WeChatSend
from tools.other_tools.allure_data.allure_report_data import AllureFileClean
from tools.other_tools.allure_data.error_case_excel import ErrorCaseExcel
from tools.testdata.cache_data import CacheData


def run(environment):
    environment_data = YAMLReader.get_environment(environment)
    MySQLHelper(environment)
    CacheData.set('host', environment_data.host)
    CacheData.set('header', environment_data.header)
    # 从配置文件中获取项目名称
    INFO.logger.info(
        """
                         _    _         _      _____         _
          __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
         / _` | '_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
        | (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
         \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
              |_|
              开始执行{}项目...
            """.format(YAMLReader.get_project_name())
    )

    pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWarning',
                 '--alluredir', './report/tmp', "--clean-alluredir"])

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

    os.system(r"allure generate ./report/tmp -o ./report/html --clean")

    allure_data = AllureFileClean().get_case_count()
    notification_mapping = {
        NotificationType.WECHAT.value: WeChatSend(allure_data, environment).send_wechat_notification,
        NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
    }
    for i in environment_data.notification_type_list:
        notification_mapping.get(i)()
    if environment_data.excel_report:
        ErrorCaseExcel().write_case()

    # 程序运行之后，自动启动报告，如果不想启动报告，可注释这段代码
    os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p 9999")


if __name__ == '__main__':
    run('pre')
