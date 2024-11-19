# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-19 11:36
# @Author : 毛鹏
from mangokit import DataProcessor
from datetime import date


class ObtainTestData(DataProcessor):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_file(cls, data):
        pass

    @classmethod
    def get_today_weekday(cls):
        """获取今天是周几（返回中文）"""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday = date.today().weekday()
        return weekdays[weekday]


if __name__ == '__main__':
    today_weekday = ObtainTestData.get_today_weekday()
    print(f"今天是: {today_weekday}")
