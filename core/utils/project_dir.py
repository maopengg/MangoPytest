# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-03-05 20:39
# @Author : 毛鹏

import os
from pathlib import Path

from core.runtime import runtime_root


class ProjectDir:

    def __init__(self):
        self._root_path = self.init_project_path()
        self._runtime_path = str(runtime_root(self._root_path))
        self.folder_list = [
            "reports",
            "downloads",
            "screenshots",
            "generated_cases",
            "logs",
            "cache",
            "temp",
        ]
        self.init_folder()

    @staticmethod
    def init_project_path():

        return Path(__file__).resolve().parent.parent.parent

    def init_folder(self):
        for i in self.folder_list:
            subdirectory = os.path.join(self._runtime_path, i)
            os.makedirs(subdirectory, exist_ok=True)

    def root_path(self):
        return self._root_path

    def cache_file(self):
        return os.path.join(self.cache(), 'cache.db')

    def cache(self):
        return os.path.join(self._runtime_path, "cache")

    def report(self, folder_name="allure"):
        return os.path.join(self._runtime_path, "reports", folder_name)

    def reports(self, folder_name=""):
        return os.path.join(self._runtime_path, "reports", folder_name)

    def logs(self, folder_name=""):
        return os.path.join(self._runtime_path, "logs", folder_name)

    def download(self, folder_name=""):
        return os.path.join(self._runtime_path, "downloads", folder_name)

    def screenshot(self, folder_name=""):
        return os.path.join(self._runtime_path, "screenshots", folder_name)


project_dir = ProjectDir()
