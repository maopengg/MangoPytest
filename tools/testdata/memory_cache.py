# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-05-24 22:35
# @Author : 毛鹏
from diskcache import Cache

from config.setting import root_path


class CacheData:
    cache = Cache(root_path())

    @classmethod
    def get(cls, key):
        """
        获取缓存中指定键的值

        参数：
        - key: 缓存键

        返回：
        - 缓存键对应的值，若键不存在则返回None
        """
        return cls.cache.get(key)

    @classmethod
    def set(cls, key, value):
        """
        设置缓存键的值

        参数：
        - key: 缓存键
        - value: 缓存值
        """
        cls.cache.set(key, value)

    @classmethod
    def delete(cls, key):
        """
        删除缓存中指定键的值

        参数：
        - key: 缓存键
        """
        cls.cache.delete(key)

    @classmethod
    def update(cls, key, value):
        """
        更新缓存键的值

        如果缓存中存在指定键，则更新其对应的值；如果不存在，则不进行任何操作。

        参数：
        - key: 缓存键
        - value: 缓存值
        """
        if key in cls.cache:
            cls.cache[key] = value

    @classmethod
    def contains(cls, key):
        """
        检查缓存中是否包含指定键

        参数：
        - key: 缓存键

        返回：
        - 如果缓存中包含指定键，返回True；否则返回False
        """
        return key in cls.cache

    @classmethod
    def clear(cls):
        """
        清空缓存中的所有键值对
        """
        cls.cache.clear()


if __name__ == '__main__':
    # 示例用法
    CacheData.set('name', 'John')
    print(CacheData.get('name'))  # 输出: John
    CacheData.update('name', 'Alice')
    print(CacheData.get('name'))  # 输出: Alice
    CacheData.delete('name')
    print(CacheData.get('name'))  # 输出: None
    print(CacheData.contains('name'))  # 输出: False
