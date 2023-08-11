# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏

import time
from datetime import datetime
from typing import Text


class TimeTools:
    """时间处理类"""

    @classmethod
    def count_milliseconds(cls) -> str:
        """
        计算时间
        :return:
        """
        access_start = datetime.now()
        access_end = datetime.now()
        access_delta = (access_end - access_start).seconds * 1000
        return access_delta

    @classmethod
    def timestamp_conversion(cls, time_str: Text) -> int:
        """
        时间戳转换，将日期格式转换成时间戳
        :param time_str: 时间
        :return:
        """

        try:
            datetime_format = datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S")
            timestamp = int(
                time.mktime(datetime_format.timetuple()) * 1000.0
                + datetime_format.microsecond / 1000.0
            )
            return timestamp
        except ValueError as exc:
            raise ValueError('日期格式错误, 需要传入得格式为 "%Y-%m-%d %H:%M:%S" ') from exc

    @classmethod
    def time_conversion(cls, time_num: int) -> str:
        """
        时间戳转换成日期
        :param time_num:
        :return:
        """
        if isinstance(time_num, int):
            time_stamp = float(time_num / 1000)
            time_array = time.localtime(time_stamp)
            other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            return other_style_time

    @classmethod
    def now_time(cls) -> str:
        """
        获取当前时间, 日期格式: 2021-12-11 12:39:25
        :return:
        """
        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return localtime

    @classmethod
    def now_time_day(cls) -> str:
        """
        获取当前时间, 日期格式: 2021-12-11
        :return:
        """
        localtime = time.strftime("%Y-%m-%d", time.localtime())
        return localtime

    @classmethod
    def get_time_for_min(cls, minute: int) -> int:
        """
        获取几分钟后的时间戳
        @param minute: 分钟
        @return: N分钟后的时间戳
        """
        return int(time.time() + 60 * minute) * 1000

    @classmethod
    def get_now_time(cls) -> int:
        """
        获取当前时间戳, 整形
        @return: 当前时间戳
        """
        return int(time.time()) * 1000
