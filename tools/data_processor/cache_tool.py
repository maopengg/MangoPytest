# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-05-24 22:35
# @Author : 毛鹏
from diskcache import Cache

from config.settings import CACHE_PATH
from models.tools_model import MysqlDBModel


class CacheTool:
    """缓存数据处理类"""
    cache = Cache(CACHE_PATH)

    @classmethod
    def cache_get(cls, key: str) -> str | list | dict:
        """
        获取缓存中指定键的值
        :param key: 缓存键
        :return:
        """
        return cls.cache.get(key)

    @classmethod
    def cache_set(cls, key: str, value: str | list | dict | MysqlDBModel) -> None:
        """
        设置缓存键的值
        :param key: 缓存键
        :param value: 缓存值
        :return:
        """
        cls.cache.set(key, value)

    @classmethod
    def cache_delete(cls, key: str) -> None:
        """
        删除缓存中指定键的值
        :param key: 缓存键
        :return:
        """
        cls.cache.delete(key)

    @classmethod
    def cache_update(cls, key: str, value: str | list | dict) -> None:
        """
        更新缓存键的值
        如果缓存中存在指定键，则更新其对应的值；如果不存在，则不进行任何操作。
        :param key: 缓存键
        :param value: 缓存值
        :return:
        """
        if key in cls.cache:
            cls.cache[key] = value

    @classmethod
    def cache_contains(cls, key: str) -> bool:
        """
        检查缓存中是否包含指定键
        :param key: 缓存键
        :return: 如果缓存中包含指定键，返回True；否则返回False
        """
        return key in cls.cache

    @classmethod
    def cache_clear(cls) -> None:
        """
        清空缓存中的所有键值对
        :return:
        """
        cls.cache.clear()


if __name__ == '__main__':
    # 示例用法
    CacheTool.cache_set('name', 'John')
    print(CacheTool.cache_get('name'))  # 输出: John
    CacheTool.cache_update('name', 'Alice')
    print(CacheTool.cache_get('name'))  # 输出: Alice
    CacheTool.cache_delete('name')
    print(CacheTool.cache_get('name'))  # 输出: None
    print(CacheTool.cache_contains('name'))  # 输出: False
