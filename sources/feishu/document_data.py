# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 22:11
# @Author : 毛鹏
import json
import os.path

import pandas
import pandas as pd
import requests
from mangotools.enums import NoticeEnum

from enums.api_enum import MethodEnum
from enums.tools_enum import EnvironmentEnum, ClientEnum, StatusEnum
from enums.ui_enum import ElementExpEnum
from exceptions import ToolsError, ERROR_MSG_0351
from models.tools_model import FeiShuModel
from tools import project_dir


class DocumentData:

    def __init__(self):
        with open(os.path.join(project_dir.root_path(), 'settings', 'feishu.json'), 'r', encoding='utf-8') as f:
            self.config = FeiShuModel(**json.load(f))
        self.url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/"
        self.parameter = "&valueRenderOption=ToString&dateTimeRenderOption=FormattedString"
        self.headers = {
            'Authorization': 'Bearer t-g10442ey6YHQCZAF6EBJB4CCSJTGCOUM6N3GJ2CF',
            'Content-Type': 'application/json; charset=utf-8'
        }
        self.status_enum = {v: k for k, v in StatusEnum.obj().items()}
        self.get_token()

    def get_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = json.dumps({
            "app_id": self.config.app_id,
            "app_secret": self.config.app_secret
        })

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=payload, proxies={'http': None, 'https': None})
        self.headers['Authorization'] = f'Bearer {response.json()["tenant_access_token"]}'

    def get_sheet(self, spreadsheet_token) -> list:
        response = requests.get(
            f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query',
            headers=self.headers,
            proxies={'http': None, 'https': None}
        )
        return response.json()['data']['sheets']

    def project(self):
        for i in self.config.surface.project.sheet:
            if i.title == '项目信息':
                url = f"{self.url}{self.config.surface.project.id}/values_batch_get?ranges={i.id}{self.parameter}"
                df = self.cls(url)
                df = df.rename(columns={
                    'ID': 'id',
                    '名称': 'name'
                })
                return df

    def notice_config(self):
        for i in self.config.surface.project.sheet:
            if i.title == '通知配置':
                url = f"{self.url}{self.config.surface.project.id}/values_batch_get?ranges={i.id}{self.parameter}"
                df = self.cls(url)
                df['类型'] = df['类型'].map({v: k for k, v in NoticeEnum.obj().items()})
                df = df.rename(columns={
                    'ID': 'id',
                    '项目名称': 'project_name',
                    '类型': 'type',
                    '配置': 'config'
                })

                return df

    def test_object(self):
        for i in self.config.surface.project.sheet:
            if i.title == '测试环境':
                url = f"{self.url}{self.config.surface.project.id}/values_batch_get?ranges={i.id}{self.parameter}"
                df = self.cls(url)
                df['环境类型'] = df['环境类型'].map(EnvironmentEnum.reversal_obj())
                df['客户端类型'] = df['客户端类型'].map(ClientEnum.reversal_obj())
                df['是否通知'] = df['是否通知'].map(StatusEnum.reversal_obj())
                df['是否默认使用'] = df['是否默认使用'].map(StatusEnum.reversal_obj())
                df['数据库-查询'] = df['数据库-查询'].map(StatusEnum.reversal_obj())
                df['数据库-增删改'] = df['数据库-增删改'].map(StatusEnum.reversal_obj())
                df = df.rename(columns={
                    'ID': 'id',
                    '项目名称': 'project_name',
                    '环境类型': 'type',
                    '名称': 'name',
                    '客户端类型': 'client_type',
                    '是否默认使用': 'is_use',
                    '是否通知': 'is_notice',
                    '数据库-查询': 'db_c_status',
                    '数据库-增删改': 'db_rud_status',
                })
                return df

    def api_info(self):
        df_list = []
        for i in self.get_sheet(self.config.surface.api_info_id):
            url = f"{self.url}{self.config.surface.api_info_id}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
            df = self.cls(url)
            df['客户端类型'] = df['客户端类型'].map(ClientEnum.reversal_obj())
            df['请求方法'] = df['请求方法'].map(MethodEnum.reversal_obj())
            df = df.rename(columns={
                'ID': 'id',
                '项目名称': 'project_name',
                '接口名称': 'name',
                '客户端类型': 'client_type',
                '请求方法': 'method',
                '请求头': 'headers',
            })
            df_list.append(df)
        combined_df = pandas.concat(df_list, ignore_index=True)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=("接口信息表",))
        return combined_df

    def api_test_case(self):
        df_list = []
        for i in self.get_sheet(self.config.surface.api_test_case_id):
            url = f"{self.url}{self.config.surface.api_test_case_id}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
            df = self.cls(url)
            df = df.rename(columns={
                'ID': 'id',
                '项目名称': 'project_name',
                '用例名称': 'name',
            })
            df_list.append(df)
        combined_df = pandas.concat(df_list, ignore_index=True)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('API测试用例',))

        return combined_df

    def ui_element(self):
        df_list = []
        for i in self.get_sheet(self.config.surface.ui_element_id):
            url = f"{self.url}{self.config.surface.ui_element_id}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
            df = self.cls(url)
            df['定位方式1'] = df['定位方式1'].map(ElementExpEnum.reversal_obj())
            df['定位方式2'] = df['定位方式2'].map(ElementExpEnum.reversal_obj())
            df['定位方式3'] = df['定位方式3'].map(ElementExpEnum.reversal_obj())
            df = df.rename(columns={
                'ID': 'id',
                '项目名称': 'project_name',
                '模块名称': 'module_name',
                '页面名称': 'page_name',
                '元素名称': 'ele_name',
                '定位方式1': 'method1',
                '表达式1': 'locator1',
                '下标1': 'nth1',
                '定位方式2': 'method2',
                '表达式2': 'locator2',
                '下标2': 'nth2',
                '定位方式3': 'method3',
                '表达式3': 'locator3',
                '下标3': 'nth3',
                '等待': 'sleep',
            })
            df_list.append(df)
        combined_df = pd.concat(df_list, ignore_index=True)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('UI元素表',))
        return combined_df

    def ui_test_case(self):
        df_list = []
        for i in self.get_sheet(self.config.surface.ui_test_case_id):
            url = f"{self.url}{self.config.surface.ui_test_case_id}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
            df = self.cls(url)
            df = df.rename(columns={
                'ID': 'id',
                '项目名称': 'project_name',
                '用例名称': 'name',
            })
            df_list.append(df)

        combined_df = pd.concat(df_list, ignore_index=True)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('UI测试用例',))
        return combined_df

    def other_test_case(self):
        df_list = []
        for i in self.get_sheet(self.config.surface.other_test_case_id):
            url = f"{self.url}{self.config.surface.other_test_case_id}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
            df = self.cls(url)
            df = df.rename(columns={
                'ID': 'id',
                '项目名称': 'project_name',
                '用例名称': 'name',
            })
            df_list.append(df)
        combined_df = pd.concat(df_list, ignore_index=True)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('其他类型测试用例',))
        return combined_df

    def cls(self, url):
        response = requests.get(url, headers=self.headers, proxies={'http': None, 'https': None})
        response_dict = response.json()
        if response_dict.get('code') != 0:
            response = requests.get(url, headers=self.headers, proxies={'http': None, 'https': None})
            response_dict = response.json()
        data = response_dict['data']['valueRanges'][0]['values']
        return pandas.DataFrame(data[1:], columns=data[0])


if __name__ == '__main__':
    print(DocumentData().api_test_case())
    print(DocumentData().api_info())
    print(DocumentData().ui_element())
    print(DocumentData().ui_test_case())
    print(DocumentData().other_test_case())
    print(DocumentData().project())
