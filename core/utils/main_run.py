# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-19 10:07
# @Author : 毛鹏

import os
import socket
import traceback

import pytest

from auto_tests.project_config import auto_test_project_config, set_os_environment
from core.models.tools_model import CaseRunListModel
from core.settings.settings import IS_TEST_REPORT
from core.utils.project_dir import project_dir
from core.utils.zip_files import zip_files
from core.utils import log


def cleanup_bdd_test_data():
    """清理 BDD API Mock 测试数据

    在测试执行前清理所有 AUTO_ 开头的测试数据
    """
    try:
        # 动态获取配置，确保使用正确的环境
        from auto_tests.bdd_api_mock.config import get_config

        config = get_config()
        SessionLocal = config.SessionLocal

        from auto_tests.bdd_api_mock.hooks.cleanup_hooks import TestDataCleaner

        log.info(">>> [MainRun] 执行前清理 BDD API Mock 测试数据...")
        session = SessionLocal()
        try:
            cleaner = TestDataCleaner(session)
            cleaner.clear_all()
        finally:
            session.close()
    except Exception as e:
        traceback.print_exc()
        log.warning(f">>> [MainRun] 数据清理失败: {e}")


class MainRun:

    def __init__(self, test_project: list[dict], pytest_command: list):
        self.case_run_list: CaseRunListModel = CaseRunListModel(case_run=test_project)
        os.environ["TEST_ENV"] = self.case_run_list.model_dump_json()

        # 为每个项目设置 ENV 环境变量（供 BDD 等项目使用）
        for project_config in test_project:
            project_name = project_config.get("project")
            if project_name:
                set_os_environment(project_name)

        self.pytest_command = pytest_command
        zip_files()
        self.run()

    def run(self):
        for case_run_model in self.case_run_list.case_run:
            for i in auto_test_project_config:
                if i.get(
                    "project_name"
                ) == case_run_model.project and case_run_model.type == i.get("type"):
                    # 如果是 BDD API Mock 项目，先清理数据
                    if case_run_model.project == "BDD_API_MOCK":
                        cleanup_bdd_test_data()

                    # 构建测试路径
                    test_cases_path = rf'{project_dir.root_path()}\auto_tests\{i.get("dir_name")}\test_cases'
                    features_path = rf'{project_dir.root_path()}\auto_tests\{i.get("dir_name")}\features'
                    
                    # 检查 test_cases 目录是否存在
                    if os.path.isdir(test_cases_path):
                        self.pytest_command.append(test_cases_path)
                        log.info(f">>> 添加测试路径: {test_cases_path}")
                    # 否则检查 features 目录是否存在
                    elif os.path.isdir(features_path):
                        self.pytest_command.append(features_path)
                        log.info(f">>> 添加测试路径: {features_path}")
                    else:
                        log.warning(f">>> 未找到测试目录: {test_cases_path} 或 {features_path}")

        log.info(f"开始执行测试任务......")
        log.info(f"pytest 命令: {self.pytest_command}")
        pytest.main(self.pytest_command)
        if IS_TEST_REPORT:
            os.system(r"allure generate ./report/tmp -o ./report/html --clean")
        # NoticeMain(self.case_run_list.case_run).notice_main()
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
