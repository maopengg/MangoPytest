# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2024-04-01 22:11
# @Author : 毛鹏
import json

import pandas

from enums.api_enum import MethodEnum
from enums.tools_enum import NoticeEnum, EnvironmentEnum, ClientEnum, StatusEnum
from enums.ui_enum import ElementExpEnum
from settings.settings import PROJECT, API_TEST_CASE, API_INFO, UI_ELEMENT, APP_ID, APP_SECRET


class DocumentData:

    def __init__(self):
        self.url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/"
        self.parameter = "&valueRenderOption=ToString&dateTimeRenderOption=FormattedString"
        self.headers = {
            'Authorization': 'Bearer t-g10442ey6YHQCZAF6EBJB4CCSJTGCOUM6N3GJ2CF',
            'Content-Type': 'application/json; charset=utf-8'
        }
        self.status_enum = {v: k for k, v in StatusEnum.obj().items()}

    def get_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = json.dumps({
            "app_id": APP_ID,
            "app_secret": APP_SECRET
        })

        headers = {
            'Content-Type': 'application/json'
        }
        from tools.base_request.request_tool import RequestTool
        response = RequestTool.internal_http(url, "POST", headers=headers, data=payload)
        self.headers['Authorization'] = f'Bearer {response.json()["tenant_access_token"]}'

    def project(self):
        for i in PROJECT[1]:
            if i.get('title') == '项目信息':
                url = f"{self.url}{PROJECT[0]}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
                df = self.cls(url)
                df = df.rename(columns={'ID': 'id', '名称': 'name'})
                return df

    def notice_config(self):
        for i in PROJECT[1]:
            if i.get('title') == '通知配置':
                url = f"{self.url}{PROJECT[0]}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
                df = self.cls(url)
                df['类型'] = df['类型'].map(NoticeEnum.reversal_obj())
                df = df.rename(columns={'ID': 'id', '项目ID': 'project_id', '类型': 'type', '配置': 'config'})

                return df

    def test_object(self):
        for i in PROJECT[1]:
            if i.get('title') == '测试环境':
                url = f"{self.url}{PROJECT[0]}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
                df = self.cls(url)
                df['环境类型'] = df['环境类型'].map(EnvironmentEnum.reversal_obj())
                df['客户端类型'] = df['客户端类型'].map(ClientEnum.reversal_obj())
                df['是否通知'] = df['是否通知'].map(StatusEnum.reversal_obj())
                df['数据库-查询'] = df['数据库-查询'].map(StatusEnum.reversal_obj())
                df['数据库-增删改'] = df['数据库-增删改'].map(StatusEnum.reversal_obj())
                df = df.rename(columns={'ID': 'id',
                                        '项目ID': 'project_id',
                                        '环境类型': 'type',
                                        '名称': 'name',
                                        '客户端类型': 'client_type',
                                        '是否通知': 'is_notice',
                                        '数据库-查询': 'db_c_status',
                                        '数据库-增删改': 'db_rud_status',
                                        })
                return df

    def api_info(self):
        url = f"{self.url}{API_INFO[0]}/values_batch_get?ranges={API_INFO[1][0].get('sheet_id')}{self.parameter}"
        df = self.cls(url)
        df['客户端类型'] = df['客户端类型'].map(ClientEnum.reversal_obj())
        df['请求方法'] = df['请求方法'].map(MethodEnum.reversal_obj())
        df = df.rename(columns={'ID': 'id',
                                '项目ID': 'project_id',
                                '接口名称': 'name',
                                '客户端类型': 'client_type',
                                '请求方法': 'method',
                                '请求头': 'headers',
                                })
        return df

    def api_test_case(self):
        url = f"{self.url}{API_TEST_CASE[0]}/values_batch_get?ranges={API_TEST_CASE[1][0].get('sheet_id')}{self.parameter}"
        df = self.cls(url)
        df = df.rename(columns={'ID': 'id',
                                '项目ID': 'project_id',
                                '用例名称': 'name',
                                })
        return df

    def ui_element(self):
        url = f"{self.url}{UI_ELEMENT[0]}/values_batch_get?ranges={UI_ELEMENT[1][0].get('sheet_id')}{self.parameter}"
        df = self.cls(url)
        df['定位方式'] = df['定位方式'].map(ElementExpEnum.reversal_obj())
        df = df.rename(columns={'ID': 'id',
                                '项目ID': 'project_id',
                                '模块名称': 'module_name',
                                '页面名称': 'page_name',
                                '元素名称': 'ele_name',
                                '定位方式': 'method',
                                '表达式': 'locator',
                                '下标': 'nth',
                                '等待': 'sleep',
                                })
        return df

    def cls(self, url):
        from tools.base_request.request_tool import RequestTool

        response = RequestTool.internal_http(url, "GET", headers=self.headers)
        response_dict = response.json()
        if response_dict.get('code') != 0:
            self.get_token()
            response = RequestTool.internal_http(url, "GET", headers=self.headers)
            response_dict = response.json()
        data = response_dict['data']['valueRanges'][0]['values']
        return pandas.DataFrame(data[1:], columns=data[0])


if __name__ == '__main__':
    print(DocumentData().ui_element())
    print(DocumentData().api_test_case())
