# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import json

import allure
from requests.models import Response


def around(api_name: str):
    """
    响应统一处理
    @return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            response: Response = func(*args, **kwargs)
            allure.attach(
                f"args: {', '.join(str(arg) for arg in args[:1])},"
                f"kwargs: {', '.join(f'{key}={val}' for key, val in kwargs.items())}",
                f'{api_name}->请求参数')
            allure.attach(str(response.status_code), f'{api_name}->响应状态码')
            allure.attach(str(json.dumps(response.json(), ensure_ascii=False)), f'{api_name}->响应结果')
            return response

        return wrapper

    return decorator
