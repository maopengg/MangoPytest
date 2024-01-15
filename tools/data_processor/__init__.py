# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import re

from exceptions.exception import CacheIsNone
from tools.data_processor.cache_tool import CacheTool
from tools.data_processor.coding_tool import CodingTool
from tools.data_processor.encryption_tool import EncryptionTool
from tools.data_processor.excel_tool import ExcelTools
from tools.data_processor.json_tool import JsonTool
from tools.data_processor.random_tool import RandomTool
from tools.data_processor.time_tool import TimeTools


class DataProcessor(JsonTool, RandomTool, CacheTool, EncryptionTool, TimeTools, CodingTool, ExcelTools):
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
            value = cls.get_cache(key_value)
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
                cls.set_cache(key_value, value)
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
                value = cls.get_cache(res2)
                if value:
                    data1 = re.sub(pattern=r"\${}".format("{" + res2 + "}"), repl=str(value), string=data1)
                else:
                    raise CacheIsNone("缓存中的值是null，请检查依赖")

    @classmethod
    def remove_parentheses(cls, data: str) -> str:
        res1 = data.replace("${", "")
        res2 = res1.replace("}", "")
        return res2


if __name__ == '__main__':
    DataProcessor.set_cache('test_note_05_id', 109)
    print(DataProcessor.get_cache('test_note_05_id'))
    data = {"pid": "${test_note_05_id}", "classificationId": 2}
    print(DataProcessor.replace_text(str(data)))
