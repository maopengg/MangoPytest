# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-19 11:36
# @Author : 毛鹏
from datetime import date, datetime, timedelta

from mangokit import DataProcessor

from tools.project_path.project_path import ProjectPaths


class ObtainTestData(DataProcessor):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_file(cls, project_name, file_name):
        """获取文件地址"""
        project_path = ProjectPaths.get_project_path(project_name)
        return f'{project_path}/{file_name}'




if __name__ == '__main__':
    today_weekday = ObtainTestData.get_today_weekday()
    print(f"今天是: {today_weekday}")
