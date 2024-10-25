# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-05-06 10:35
# @Author : 毛鹏
import asyncio
import time

import allure
import pytest

from tools.log_collector import log


class TestDemo:
    @pytest.mark.asyncio
    @allure.title('英文翻译成中文')
    async def test_async_function1(self):
        # 异步测试代码
        log.info('1')
        time.sleep(5)

    @pytest.mark.asyncio
    @allure.title('英文翻译成中文')
    async def test_async_function2(self):
        # 异步测试代码
        log.info('2')
        time.sleep(5)

    @pytest.mark.asyncio
    @allure.title('英文翻译成中文')
    async def test_async_function3(self):
        # 异步测试代码
        log.info('3')
        time.sleep(5)
