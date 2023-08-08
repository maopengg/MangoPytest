# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 封装请求
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import json
import time

import requests


class HTTPRequest:

    @classmethod
    def http_get(cls,
                 url: str,
                 headers: str) -> tuple[ClientResponse, float]:
        headers = json.loads(headers)
        s = time.time()
        response = requests.get(url, headers=headers)
        response_time = time.time() - s
        return response, response_time

    @classmethod
    def http_post(cls,
                  url: str,
                  headers: str,
                  data=None) -> tuple[ClientResponse, float]:
        headers = json.loads(headers)
        s = time.time()
        response = requests.post(url, data=data, headers=headers)
        response_time = time.time() - s
        return response, response_time

    @classmethod
    def http_delete(cls,
                    url: str,
                    headers: str,
                    params=None) -> tuple[ClientResponse, float]:
        headers = json.loads(headers)
        s = time.time()
        response = requests.delete(url, params=params, headers=headers)
        response_time = time.time() - s
        return response, response_time

    @classmethod
    def http_put(cls,
                 url: str,
                 headers: str,
                 data=None) -> tuple[ClientResponse, float]:
        headers = json.loads(headers)
        s = time.time()
        response = requests.put(url, data=data, headers=headers)
        response_time = time.time() - s
        return response, response_time
