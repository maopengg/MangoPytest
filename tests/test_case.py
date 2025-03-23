# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-05-06 10:35
# @Author : 毛鹏
import allure
import time

from tools.log import log


class TestDemo:
    @allure.title('英文翻译成中文')
    def test_async_function1(self):
        # 异步测试代码
        log.info('1')
        time.sleep(5)

    @allure.title('英文翻译成中文')
    def test_async_function2(self):
        # 异步测试代码
        log.info('2')
        time.sleep(5)

    @allure.title('英文翻译成中文')
    def test_async_function3(self):
        # 异步测试代码
        log.info('3')
        time.sleep(5)
