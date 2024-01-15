# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2023-09-11 21:45
# @Author : 毛鹏
import json

import allure
from requests import Response

from models.api_model import ApiInfoModel
from project import TEST_PROJECT_MYSQL
from tools.request_tool.request_tool import RequestTool


def request_(*args, api_id: int, headers: dict = None, ) -> Response:
    sql = f'select * from SELECT * FROM `api_info` WHERE id = {api_id};'
    query: dict = TEST_PROJECT_MYSQL.execute_query(sql)[0]
    api_info = ApiInfoModel(**query)

    headers = api_info.headers if not headers else headers
    response: Response = RequestTool.http_post(api_info.url, headers=headers, json=api_info.body)

    allure.attach(str(api_info.url), f'{api_info.name}->url')
    allure.attach(str(headers), f'{api_info.name}->请求头')
    allure.attach(str(args), f'{api_info.name}->请求参数')
    allure.attach(str(response.status_code), f'{api_info.name}->响应状态码')
    allure.attach(str(json.dumps(response.json(), ensure_ascii=False)), f'{api_info.name}->响应结果')

    return response
