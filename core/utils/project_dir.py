# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-03-05 20:39
# @Author : 毛鹏

import os
from pathlib import Path


class ProjectDir:

    def __init__(self):
        self._root_path = self.init_project_path()
        self._artifact_path = os.path.join(self._root_path, "artifacts")
        self.folder_list = [
            "reports",
            "downloads",
            "screenshots",
            "generated_cases",
            os.path.join("temp", "logs"),
            os.path.join("temp", "cache"),
        ]
        self.init_folder()

    @staticmethod
    def init_project_path():

        return Path(__file__).resolve().parent.parent.parent

    def init_folder(self):
        for i in self.folder_list:
            subdirectory = os.path.join(self._artifact_path, i)
            if not os.path.exists(subdirectory):
                os.makedirs(subdirectory)

    def root_path(self):
        return self._root_path

    def cache_file(self):
        return os.path.join(self.cache(), 'cache.db')

    def cache(self):
        return os.path.join(self._artifact_path, "temp", "cache")

    def report(self, folder_name="allure"):
        return os.path.join(self._artifact_path, "reports", folder_name)

    def reports(self, folder_name=""):
        return os.path.join(self._artifact_path, "reports", folder_name)

    def logs(self, folder_name=""):
        return os.path.join(self._artifact_path, "temp", "logs", folder_name)

    def download(self, folder_name=""):
        return os.path.join(self._artifact_path, "downloads", folder_name)

    def screenshot(self, folder_name=""):
        return os.path.join(self._artifact_path, "screenshots", folder_name)


project_dir = ProjectDir()
