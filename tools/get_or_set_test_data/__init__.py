# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import re

from exceptions.exception import CacheIsNone
from tools.get_or_set_test_data.cache_tool import CacheTool
from tools.get_or_set_test_data.encryption_or_encoding_tool import EncryptionOrEncodingTool
from tools.get_or_set_test_data.json_tool import JsonTool
from tools.get_or_set_test_data.random_tool import RandomTool
from tools.get_or_set_test_data.time_tool import TimeTools


class GetOrSetTestData(JsonTool, RandomTool, CacheTool, EncryptionOrEncodingTool, TimeTools):
    """
    测试数据处理类汇总
    """

    @classmethod
    def case_input_data(cls, obj, ope_value: str, key: str = None) -> str:
        """
        取出缓存或写入
        :param obj:
        :param ope_value:
        :param key:
        :return:
        """
        if key:
            key_value = str(id(obj)) + str(key)
            value = cls.cache_get(key_value)
        else:
            key_value = str(id(obj))
            value = None
        # 缓存为空的时候进行读取数据并写入缓存
        if value is None:
            if ope_value:
                if "()" in ope_value:
                    value = cls.random_regular(ope_value)
                elif ope_value:
                    value = ope_value
            if key:
                cls.cache_set(key_value, value)
        return value

    @classmethod
    def replace_text(cls, data: str) -> str:
        """
        用来替换包含${}文本信息，通过读取缓存中的内容，完成替换（可以是任意格式的文本）
        @param data: 需要替换的文本
        @return: 返回替换完成的文本
        """
        data1 = data
        while True:
            rrr = re.findall(r"\${.*?}", data1)
            if not rrr:
                return data1
            res1 = rrr[0].replace("${", "")
            res2 = res1.replace("}", "")
            # 获取随机数据，完成替换
            if "()" in res2:
                value = cls.random_regular(res2)
                res3 = res2.replace("()", "")
                data1 = re.sub(pattern=r"\${}".format("{" + res3 + r"\(\)" + "}"), repl=value, string=data1)
            # 获取缓存数据，完成替换
            else:
                # value = Cache().read_data_from_cache(res2)
                value = cls.cache_get(res2)
                if value:
                    data1 = re.sub(pattern=r"\${}".format("{" + res2 + "}"), repl=value, string=data1)
                else:
                    raise CacheIsNone("缓存中的值是null，请检查依赖")
