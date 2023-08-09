# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
from requests.models import Response

from exceptions.exception import AssertionFailure


def around():
    """
    转换类型装饰器
    @param set_type:
    @return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            response: Response = func(*args, **kwargs)
            # assert response.status_code != 500
            # if response.status_code != 200 and response.status_code != 300:
            #     raise AssertionFailure(f"公共断言失败，请求失败，code码：{response.status_code}")

            return response

        return wrapper

    return decorator
