# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-19 10:07
# @Author : 毛鹏

import os
import socket
import pytest
import importlib
import json
from core.enums.tools_enum import EnvironmentEnum
from core.models.tools_model import CaseRunModel
from core.settings.settings import IS_TEST_REPORT
from core.utils import log
from core.utils.notice import NoticeMain
from core.utils.project_dir import project_dir
from core.utils.zip_files import zip_files


class MainRun:

    def __init__(self, project_config: dict, pytest_command: list):
        self.project = CaseRunModel(**project_config)
        os.environ["TEST_ENV"] = json.dumps(
            [self.project.model_dump(mode="json")]
        )
        self.base_pytest_command = pytest_command
        zip_files()

    _REQUIRED_ATTRS = [
        "PROJECT_NAME", "PROJECT_TYPE", "DEFAULT_ENV",
        "PROJECT_DISPLAY_NAME", "NOTICE_CHANNEL", "NOTICE_EMAIL_SEND_LIST",
        "NOTICE_WECHAT_WEBHOOK", "NOTICE_FEISHU_WEBHOOK",
    ]

    def _get_project_module(self):
        """动态导入项目 __init__.py，校验必要配置"""
        try:
            proj = importlib.import_module(f"auto_tests.{self.project.project}")
        except ImportError:
            raise ImportError(
                f"项目 '{self.project.project}' 不存在，"
                f"请确认 auto_tests/{self.project.project}/__init__.py 文件存在"
            )

        missing = [a for a in self._REQUIRED_ATTRS if not hasattr(proj, a)]
        if missing:
            raise AttributeError(
                f"项目 '{self.project.project}' 的 __init__.py 缺少必需配置: {missing}\n"
                f"请参考 auto_tests/qfei_contract_api/__init__.py"
            )
        return proj

    def main(self):
        dir_name = self.project.project
        env_str = self.project.test_environment.name.lower()
        os.environ["ENV"] = env_str

        proj = self._get_project_module()

        base = os.path.join(project_dir.root_path(), "auto_tests", dir_name)
        candidates = [
            os.path.join(base, "test_cases"),
            os.path.join(base, "features"),
        ]

        cmd = list(self.base_pytest_command)
        test_path = None
        for p in candidates:
            if os.path.isdir(p):
                test_path = p
                break

        if not test_path:
            log.error(f">>> 未找到测试目录, 尝试了: {candidates}")
            return
        cmd.append(test_path)

        log.info(f">>> [{dir_name}] ENV={env_str}")
        log.info(f">>> [{dir_name}] pytest 命令: {cmd}")
        log.info(f">>> [{dir_name}] 开始执行...")

        pytest.main(cmd)

        if IS_TEST_REPORT:
            os.system(r"allure generate ./report/tmp -o ./report/html --clean")

        if proj:
            display_name = getattr(proj, "PROJECT_DISPLAY_NAME", dir_name)
            NoticeMain(dir_name, display_name, env_str, proj).notice_main()

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
