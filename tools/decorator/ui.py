# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-08-14 14:05
# @Author : 毛鹏
import allure
import pytest

def case_data(title, parametrize_data):
    def decorator(func):
        @allure.title(title)
        @pytest.mark.parametrize("data", parametrize_data)
        @pytest.mark.asyncio
        async def wrapper(self, setup_context_page, data):
            # 根据参数数量动态选择参数
            return await func(self, await setup_context_page, data)

        return wrapper

    return decorator
