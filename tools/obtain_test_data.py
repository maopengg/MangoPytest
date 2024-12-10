# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-19 11:36
# @Author : 毛鹏
from datetime import date

from mangokit import DataProcessor


class ObtainTestData(DataProcessor):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_file(cls, data):
        pass

    @classmethod
    def time_now_hms(cls):
        """时分秒"""
        return datetime.now().strftime("%H:%M:%S")

    @classmethod
    def time_cron_time(cls, **kwargs) -> str:
        time_parts = kwargs.get('data').split()
        seconds = int(time_parts[0])
        minutes = int(time_parts[1])
        hours = int(time_parts[2])
        current_date = datetime.now().date()
        date_obj = datetime(year=current_date.year,
                            month=current_date.month,
                            day=current_date.day,
                            hour=hours,
                            minute=minutes,
                            second=seconds)

        time_str_result = date_obj.strftime("%H:%M:%S")
        return time_str_result

    @classmethod
    def time_next_minute_cron(cls, **kwargs):
        """按周重复的cron表达式"""
        if kwargs.get('data'):
            minutes = int(kwargs.get('data'))
        else:
            minutes = 1
        now = datetime.now() + timedelta(minutes=minutes)
        second = f"{now.second:02d}"  # 格式化为两位数
        minute = f"{now.minute:02d}"  # 格式化为两位数
        hour = f"{now.hour:02d}"  # 格式化为两位数
        day = "?"  # 日用问号表示不指定
        month = "*"  # 月用星号表示每个月
        weekday = str(date.today().weekday() + 2)
        return f"{second} {minute} {hour} {day} {month} {weekday}"


if __name__ == '__main__':
    today_weekday = ObtainTestData.get_today_weekday()
    print(f"今天是: {today_weekday}")
