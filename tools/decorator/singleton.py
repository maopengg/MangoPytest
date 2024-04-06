# -*- coding: utf-8 -*-
# @Project: 单例模式
# @Description: 
# @Time   : 2023/4/26 17:41
# @Author : 毛鹏
import threading


def singleton(cls):
    """
    单例模式
    @param cls:类对象
    @return:
    """
    _instance = {}
    _lock = threading.Lock()  # 添加一个锁

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            with _lock:
                if cls not in _instance:  # 确保在加锁的情况下再次检查
                    _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton
