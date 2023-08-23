# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import allure
from requests.models import Response


def around():
    """
    转换类型装饰器
    @return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            response: Response = func(*args, **kwargs)
            # assert response.status_code != 500
            # if response.status_code != 200 and response.status_code != 300:
            #     raise AssertionFailure(f"公共断言失败，请求失败，code码：{response.status_code}")
            allure.attach(
                f"args: {', '.join(str(arg) for arg in args[:1])},"
                f" kwargs: {', '.join(f'{key}={val}' for key, val in kwargs.items())}",
                "请求参数", )
            allure.attach(str(response.status_code), "响应状态码")
            allure.attach(str(response.json()), "响应结果")
            return response

        return wrapper

    return decorator
