# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 15:30
# @Author : 毛鹏

import allure
import pytest

from auto_test.api.baidu_translate.modules_api.translate import TranslateApi
from models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.data_processor import DataProcessor
from tools.decorator.response import case_data


@allure.epic('百度翻译')
@allure.feature('对接百度翻译接口')
class TestTranslate(TranslateApi, CaseTool):
    data_processor: DataProcessor = DataProcessor()

    @allure.title('英文翻译成中文')
    @case_data(4)
    def test_login01(self, data: ApiDataModel):
        appid = self.data_model.cache_data.get('app_id')
        secret_key = self.data_model.cache_data.get('secret_key')
        salt = self.data_processor.randint(32768, 65536)
        query = data.test_case.params.get('q')
        sign = self.data_processor.md5_32_small(appid + query + str(salt) + secret_key)
        data.test_case.params['appid'] = appid
        data.test_case.params['salt'] = salt
        data.test_case.params['sign'] = sign
        data = self.case_run(self.translate, data)
        assert data.response.response_dict['trans_result'][0]['dst'] == "芒果"
        assert data.response.response_dict['trans_result'][0]['src'] == "mango"

    @allure.title('中文翻译成英文')
    @case_data(5)
    def test_login02(self, data: ApiDataModel):
        appid = self.data_model.cache_data.get('app_id')
        secret_key = self.data_model.cache_data.get('secret_key')
        salt = self.data_processor.randint(32768, 65536)
        query = data.test_case.params.get('q')
        sign = self.data_processor.md5_32_small(appid + query + str(salt) + secret_key)
        data.test_case.params['appid'] = appid
        data.test_case.params['salt'] = salt
        data.test_case.params['sign'] = sign
        data = self.case_run(self.translate, data)
        assert data.response.response_dict['trans_result'][0]['src'] == "芒果"
        assert data.response.response_dict['trans_result'][0]['dst'] == "mango"


if __name__ == '__main__':
    pytest.main(
        [r'D:\GitCode\PytestAutoTest\auto_test\api\baidu_translate\test_case\test_translate.py::TestTranslate'])
