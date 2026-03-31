# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据序列生成器
# @Time   : 2026-03-31
# @Author : 毛鹏
import time
import random
import string
from datetime import datetime
from threading import Lock


class SequenceGenerator:
    """
    序列号生成器
    用于生成各种流水号、编号等
    """

    _counters: dict = {}
    _lock: Lock = Lock()

    @classmethod
    def generate(cls, prefix: str = "SEQ", length: int = 6) -> str:
        """
        生成序列号
        @param prefix: 前缀
        @param length: 数字长度
        @return: 序列号
        """
        with cls._lock:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            if prefix not in cls._counters:
                cls._counters[prefix] = 0
            cls._counters[prefix] += 1
            counter = str(cls._counters[prefix]).zfill(length)
            return f"{prefix}{timestamp}{counter}"

    @classmethod
    def reset(cls, prefix: str = None):
        """
        重置计数器
        @param prefix: 指定前缀，不传则重置所有
        """
        with cls._lock:
            if prefix:
                cls._counters[prefix] = 0
            else:
                cls._counters.clear()

    @staticmethod
    def generate_order_no() -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"ORD{timestamp}{random_str}"

    @staticmethod
    def generate_product_code() -> str:
        """生成产品编码"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"PRD{timestamp}{random_str}"

    @staticmethod
    def generate_user_code() -> str:
        """生成用户编码"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"USR{timestamp}{random_str}"

    @staticmethod
    def generate_file_name(extension: str = "txt") -> str:
        """生成文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = ''.join(random.choices(string.ascii_lowercase, k=4))
        return f"file_{timestamp}_{random_str}.{extension}"
