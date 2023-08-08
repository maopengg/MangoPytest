# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:48
# @Author : 毛鹏
from requests.models import Response

from exceptions.exceptions import AssertionFailure


def response_data(set_type):
    """
    转换类型装饰器
    @param set_type:
    @return:
    """

    def decorator(func):
        def wrapper(*args, **kwargs) -> set_type:
            response: Response = func(*args, **kwargs)
            data = response.json()
            if response.status_code != 200 and response.status_code != 300:
                raise AssertionFailure(f"公共断言失败，请求失败，code码：{response.status_code}")
            response = set_type(code=response.status_code,
                                headers=response.headers,
                                url=response.url,
                                data=data.get('data'),
                                status=data.get('status'),
                                message=data.get('message'))

            return response

        return wrapper

    return decorator
