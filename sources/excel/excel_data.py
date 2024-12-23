# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 22:11
# @Author : 毛鹏

import pandas as pd

from enums.api_enum import MethodEnum
from enums.tools_enum import NoticeEnum, EnvironmentEnum, ClientEnum, StatusEnum
from enums.ui_enum import ElementExpEnum
from tools import InitPath


class ExcelData:

    def __init__(self):
        pass

    def project(self):
        df = self.cls(fr'{InitPath.project_root_directory}/sources/excel/项目基础信息.xlsx', '项目信息')
        df = df.rename(columns={
            'ID': 'id',
            '名称': 'name'
        })
        return df

    def notice_config(self):
        df = self.cls(fr'{InitPath.project_root_directory}/sources/excel/项目基础信息.xlsx', '通知配置')
        df['类型'] = df['类型'].map(NoticeEnum.reversal_obj())
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '类型': 'type',
            '配置': 'config'
        })
        return df

    def test_object(self):
        df = self.cls(fr'{InitPath.project_root_directory}/sources/excel/项目基础信息.xlsx', '测试环境')
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
        df = self.cls(fr'{InitPath.project_root_directory}/sources/excel/接口信息.xlsx')
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
        return df

    def api_test_case(self):
        df = self.cls(fr'{InitPath.project_root_directory}/sources/excel/API测试用例.xlsx')
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '用例名称': 'name',
        })
        return df

    def ui_element(self):
        df = self.cls(fr'{InitPath.project_root_directory}/sources/excel/元素表.xlsx')
        df['定位方式'] = df['定位方式'].map(ElementExpEnum.reversal_obj())
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '模块名称': 'module_name',
            '页面名称': 'page_name',
            '元素名称': 'ele_name',
            '定位方式': 'method',
            '表达式': 'locator',
            '下标': 'nth',
            '等待': 'sleep',
        })
        return df

    def ui_test_case(self):
        df = self.cls(fr'{InitPath.project_root_directory}/sources/excel/UI测试用例.xlsx')
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '用例名称': 'name',
        })
        return df

    def cls(self, file_path: str, sheet_name=None):
        if sheet_name is None:
            df = pd.read_excel(file_path)
        else:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df.map(lambda x: None if pd.isna(x) else x)


if __name__ == '__main__':
    print(ExcelData().api_test_case())
