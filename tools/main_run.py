# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-19 10:07
# @Author : 毛鹏

import os
import pytest
from mangokit.tools.other.native_ip import get_host_ip

from exceptions import *
from models.tools_model import CaseRunListModel
from settings.settings import IS_TEST_REPORT
from tools.files.zip_files import zip_files
from tools.log import log
from tools.notice import NoticeMain
from tools.project_path.project_path import ProjectPaths


class MainRun:

    def __init__(self, test_project: list[dict], pytest_command: list):
        self.case_run_list: CaseRunListModel = CaseRunListModel(case_run=test_project)
        os.environ['TEST_ENV'] = self.case_run_list.model_dump_json()
        self.pytest_command = pytest_command
        # 压缩上一次执行结果，并且保存起来，方便后面查询
        zip_files()
        ProjectPaths.init()
        self.run()

    def run(self):
        project_type_paths = ProjectPaths.check()
        for case_run_model in self.case_run_list.case_run:
            project_key = case_run_model.project.value
            if project_key in project_type_paths:
                ProjectPaths.update(project_key, case_run_model.test_environment.value)
                if str(case_run_model.type.value) not in project_type_paths[project_key]:
                    raise ToolsError(*ERROR_MSG_0007)
                if str(case_run_model.type.value) in project_type_paths[project_key]:
                    self.pytest_command.append(project_type_paths[project_key][str(case_run_model.type.value)])
            else:
                raise ToolsError(*ERROR_MSG_0007)
        # self.pytest_command.append(r'D:\GitCode\PytestAutoTest\auto_test\api\z_tool\test_case\test_report_assistant')
        # 执行用例
        log.info(f"开始执行测试任务......")
        pytest.main(self.pytest_command)
        # 发送通知
        if IS_TEST_REPORT:
            os.system(r"allure generate ./report/tmp -o ./report/html --clean")
        NoticeMain(self.case_run_list.case_run).notice_main()
        if IS_TEST_REPORT:
            os.system(f"allure serve ./report/tmp -h {get_host_ip()} -p 9997")
