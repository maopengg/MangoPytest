# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-04 17:23
# @Author : 毛鹏
import requests
from requests.models import Response


class RequestTool:
    time = 60

    @classmethod
    def http_get(cls, url: str, headers: dict) -> Response:
        return requests.get(url=url, headers=headers, timeout=cls.time)

    @classmethod
    def http_post(cls, url: str, headers: dict, data: dict = None, json: str | dict = None) -> Response:
        return requests.post(url=url, headers=headers, data=data, json=json, timeout=cls.time)

    @classmethod
    def http_put(cls, url: str, headers: dict, data: dict = None, json: str | dict = None) -> Response:
        return requests.put(url=url, headers=headers, data=data, json=json, timeout=cls.time)

    @classmethod
    def http_delete(cls, url: str, headers: dict) -> Response:
        return requests.delete(url=url, headers=headers, timeout=cls.time)
