# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
import random

from auto_test.api.baidu_translate import BaiduTranslateModel
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.data_processor import DataProcessor
from tools.decorator.response import request_data


class TranslateApi(RequestTool):
    data_model: BaiduTranslateModel = BaiduTranslateModel()
    data_processor: DataProcessor = None

    @request_data
    def translate(self, data: ApiDataModel = None):
        url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        appid = self.data_model.cache_data.get('app_id')
        secret_key = self.data_model.cache_data.get('secret_key')
        salt = random.randint(32768, 65536)
        query = "Hello World! This is 1st paragraph"
        from_lang = 'en'
        to_lang = 'zh'
        sign = self.data_processor.md5_32_small(appid + query + str(salt) + secret_key)

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        response = self.internal_http(url=url, method="GET", headers=headers, params=payload)
        print(response.json())


if __name__ == '__main__':
    TranslateApi().translate()
