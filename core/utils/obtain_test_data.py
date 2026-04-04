# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-19 11:36
# @Author : 毛鹏
import os

from mangotools.data_processor import DataProcessor

from auto_tests.project_config import auto_test_project_config
from core.exceptions import ToolsError, ERROR_MSG_0042
from core.utils import project_dir


class ObtainTestData(DataProcessor):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_file(cls, project_name, file_name):
        """获取文件地址"""
        for i in auto_test_project_config:
            if i.get('project_name').value == project_name:
                return os.path.join(
                    project_dir.root_path(),
                    'auto_tests',
                    i.get('dir_name'),
                    'upload',
                    file_name
                )
        raise ToolsError(*ERROR_MSG_0042)


if __name__ == '__main__':
    today_weekday = ObtainTestData.time_random_weekday()
    print(f"今天是: {today_weekday}")
