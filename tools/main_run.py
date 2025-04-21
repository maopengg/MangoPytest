# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-19 10:07
# @Author : 毛鹏

import os
import socket
import webbrowser

import pytest
import time

from auto_test.project_config import auto_test_project_config
from models.tools_model import CaseRunListModel
from settings.settings import IS_TEST_REPORT
from tools import project_dir
from tools.files.zip_files import zip_files
from tools.log import log
from tools.notice import NoticeMain


class MainRun:

    def __init__(self, test_project: list[dict], pytest_command: list):
        self.case_run_list: CaseRunListModel = CaseRunListModel(case_run=test_project)
        os.environ['TEST_ENV'] = self.case_run_list.model_dump_json()
        self.pytest_command = pytest_command
        zip_files()
        self.run()

    def run(self):
        for case_run_model in self.case_run_list.case_run:
            for i in auto_test_project_config:
                if i.get('project_name') == case_run_model.project \
                        and case_run_model.type == i.get('type'):
                    self.pytest_command.append(fr'{project_dir.root_path()}\auto_test\{i.get("dir_name")}\test_case')
        log.info(f"开始执行测试任务......")
        pytest.main(self.pytest_command)
        if IS_TEST_REPORT:
            os.system(r"allure generate ./report/tmp -o ./report/html --clean")
        NoticeMain(self.case_run_list.case_run).notice_main()
        if IS_TEST_REPORT:
            os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p 9999")

    @staticmethod
    def get_local_ip():
        """获取本机内网 IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
