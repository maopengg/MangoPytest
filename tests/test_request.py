# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-06 21:14
# @Author : 毛鹏
import requests

from models.api_model import RequestModel, ResponseModel
from tools.base_request.request_tool import RequestTool


def inside_request():
    """
    内部的请求，就是debug打印的内容，可以直接放在这里进行请求
    :return:
    """
    requests1 = RequestTool()
    response: ResponseModel = requests1.http_request(RequestModel(
        **{
            'url': 'https://zdtoolpre.zalldigital.cn/api/z-tool-app/ad-market/task/status/stats',
            'method': 'GET',
            'headers': {
                'Accept': 'application/json, text/plain, */*',
                'Authorization': 'Bearer 116d239d-de12-49d2-92c0-134ef729daf6',
                'tenant_id': '14'
            },
            'params': {'requestId': 'spider:b61f8e62-f8d2-4962-ad99-bcb8d5d81922'},
            'data': None,
            'json_data': None,
            'file': None
        }))
    print(response.response_text)


def outside_request():
    """
    复制下来的请求，对比内部请求看看有啥不同，然后分析自己写的对不对，或者mango pytest项目中有没有写的不正确的地方
    :return:
    """
    url = "https://zdtoolpre.zalldigital.cn/api/z-tool-data/ad-market/task/status/stats"

    payload = {"requestId": "spider:767f6296-0cdb-4007-b042-99e8ec7240cb"}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Authorization': 'Bearer 8f3cb726-abcb-45c0-bb8b-639b64f23ce5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'Hm_lvt_f93cf7bc34efb4e4c5074b754dec8a6b=1729244465; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22862%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkxMGQ2ZjY4MjUzZWItMDA2NjQyNzBjYjY1MzRjLTI2MDAxZDUxLTIwNzM2MDAtMTkxMGQ2ZjY4MjY3MDYifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'none',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'tenant_id': '14'
    }

    response = requests.request("GET", url, headers=headers, params=payload)

    print(response.text)


if __name__ == '__main__':
    inside_request()
    outside_request()
