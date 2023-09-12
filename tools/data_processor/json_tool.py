# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-05-24 23:20
# @Author : 毛鹏
import json
from typing import IO

import jsonpath


class JsonTool:
    """json数据处理类"""

    @classmethod
    def json_load(cls, json_file: IO[str]) -> str:
        """
        将json文件转换成字符串
        :param json_file:
        :return:
        """
        return json.load(json_file)

    @classmethod
    def json_dump(cls, data: str, json_file: IO[str]) -> None:
        """
        将Python对象转换成json格式，并写入到json文件中
        :param data:
        :param json_file:
        :return:
        """
        json.dump(data, json_file)

    @classmethod
    def json_loads(cls, data: str) -> list | dict | None:
        """
        将json字符串转换为list或dict
        :param data:
        :return:
        """
        if data is None:
            return None
        return json.loads(data)

    @classmethod
    def json_dumps(cls, data: list | dict, indent=None) -> str:
        """
        将dict或list转换为json字符串
        :param data:
        :param indent:
        :return:
        """
        return json.dumps(data, indent=indent)

    @classmethod
    def json_flatten(cls, json_obj: list | dict, sep='_', prefix=''):
        """
        将嵌套的json对象展开成扁平的字典
        :param json_obj:
        :param sep:
        :param prefix:
        :return:
        """
        result = {}
        for key, value in json_obj.items():
            new_key = prefix + key
            if isinstance(value, dict):
                result.update(cls.json_flatten(value, sep, new_key + sep))
            else:
                result[new_key] = value
        return result

    @classmethod
    def json_get_path_value(cls, obj: dict | list, expr: str, index=0) -> str | list | dict:
        """
        通过jsonpath取出对应的value
        @param obj: 需要取出的对象
        @param expr: 表达式
        @param index:下标
        @return:
        """
        return jsonpath.jsonpath(obj, expr)[index]
