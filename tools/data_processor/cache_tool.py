# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-29 10:23
# @Author : 毛鹏
from cachetools import LRUCache


class CacheTool:
    cache: LRUCache = LRUCache(maxsize=500)

    @classmethod
    def get_cache(cls, key: str) -> any:
        return cls.cache.get(key)

    @classmethod
    def set_cache(cls, key: str, value: any) -> None:
        cls.cache[key] = value

    @classmethod
    def delete_cache(cls, key: str) -> None:
        if key in cls.cache:
            del cls.cache[key]

    @classmethod
    def clear_cache(cls) -> None:
        cls.cache.clear()

    @classmethod
    def has_cache(cls, key: str) -> bool:
        return key in cls.cache
