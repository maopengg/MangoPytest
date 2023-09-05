# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
import json

import allure
from pydantic import BaseModel
from requests.models import Response

from tools.logging_tool.log_control import INFO


def is_args_contain_base_model(*args):
    for arg in args:
        if isinstance(arg, BaseModel):
            return True
    return False


def around(api_name: str):
    """
    响应统一处理
    :param api_name: 接口名称
    :return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs) -> Response:
            res_args: tuple[Response, str, dict] = func(*args, **kwargs)
            response: Response = res_args[0]

            allure.attach(str(res_args[1]), f'{api_name}->url')
            allure.attach(str(res_args[2]), f'{api_name}->请求头')
            arg1 = ''
            arg2 = ''
            for arg in args[1:]:
                if isinstance(arg, BaseModel):
                    arg1 += str(arg.json())
                else:
                    arg2 += ', '.join(str(arg))
            allure.attach(f"参数A: {arg1+arg2}\n"
                          f"参数B: {', '.join(f'{key}={val}' for key, val in kwargs.items())}",
                          f'{api_name}->请求参数')
            allure.attach(str(response.status_code), f'{api_name}->响应状态码')
            allure.attach(str(json.dumps(response.json(), ensure_ascii=False)), f'{api_name}->响应结果')

            return response

        return wrapper

    return decorator
