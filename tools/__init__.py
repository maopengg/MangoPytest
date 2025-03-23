# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-03-05 20:39
# @Author : 毛鹏

import os
from pathlib import Path

import sys


class ProjectDir:

    def __init__(self):
        self.folder_list = ['logs', 'report', 'reports', 'download']
        self._root_path = self.init_project_path()
        self.init_folder()

    @staticmethod
    def init_project_path():

        return Path(__file__).resolve().parent.parent

    def init_folder(self):
        for i in self.folder_list:
            subdirectory = os.path.join(self._root_path, i)
            if not os.path.exists(subdirectory):
                os.makedirs(subdirectory)

    def root_path(self):
        if getattr(sys, 'frozen', False):
            return sys._MEIPASS
        else:
            return self._root_path

    def cache_file(self):
        return os.path.join(self.cache(), 'cache.db')

    def cache(self):
        return os.path.join(self.root_path(), 'cache')

    def report(self, folder_name='report'):
        return os.path.join(self.root_path(), folder_name)

    def reports(self, folder_name='reports'):
        return os.path.join(self.root_path(), folder_name)

    def logs(self, folder_name='logs'):
        return os.path.join(self.root_path(), folder_name)

    def download(self, folder_name='download'):
        return os.path.join(self.root_path(), folder_name)


project_dir = ProjectDir()
if __name__ == '__main__':
    print(project_dir.root_path())
    print(project_dir.download())
    print(project_dir.logs())
    print(project_dir.reports())
    print(project_dir.report())
