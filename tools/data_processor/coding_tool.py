# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-30 14:14
# @Author : 毛鹏
import base64
import json


class CodingTool:

    @classmethod
    def base64_encode(cls, data: str) -> str:
        """
        编码字符串
        :param data: 需要进行编码的字符串
        :return:
        """
        return base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')
