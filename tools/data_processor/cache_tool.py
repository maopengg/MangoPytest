# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-29 10:23
# @Author : 毛鹏

from cachetools import LRUCache


class CacheTool:
    cache: LRUCache = LRUCache(maxsize=100)

    @classmethod
    def get(cls, key: str) -> any:
        return cls.cache.get(key)

    @classmethod
    def set(cls, key: str, value: any) -> None:
        cls.cache[key] = value

    @classmethod
    def delete(cls, key: str) -> None:
        if key in cls.cache:
            del cls.cache[key]

    @classmethod
    def clear(cls) -> None:
        cls.cache.clear()

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls.cache
