# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-04-01 22:11
# @Author : 毛鹏

import pandas as pd
from mangotools.enums import NoticeEnum

from enums.api_enum import MethodEnum
from enums.tools_enum import EnvironmentEnum, ClientEnum, StatusEnum
from enums.ui_enum import ElementExpEnum
from exceptions import ToolsError, ERROR_MSG_0351
from tools import project_dir


class ExcelData:

    def __init__(self):
        pass

    def project(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/项目基础信息.xlsx', '项目信息')
        df = df.rename(columns={
            'ID': 'id',
            '名称': 'name'
        })
        return df.map(lambda x: None if pd.isna(x) else x)

    def notice_config(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/项目基础信息.xlsx', '通知配置')
        df['类型'] = df['类型'].map({v: k for k, v in NoticeEnum.obj().items()})
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '类型': 'type',
            '配置': 'config'
        })
        return df.map(lambda x: None if pd.isna(x) else x)

    def test_object(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/项目基础信息.xlsx', '测试环境')
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
        return df.map(lambda x: None if pd.isna(x) else x)

    def api_info(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/接口信息.xlsx', sheet_name=None)
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
        combined_df = df.map(lambda x: None if pd.isna(x) else x)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('接口信息',))
        return combined_df

    def api_test_case(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/API测试用例.xlsx', sheet_name=None)
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '用例名称': 'name',
        })
        combined_df = df.map(lambda x: None if pd.isna(x) else x)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('API测试用例',))
        # duplicate_ids = combined_df[combined_df.duplicated(subset=['name'], keep=False)]
        # if not duplicate_ids.empty:
        #     raise ToolsError(*ERROR_MSG_0352)
        return combined_df

    def ui_element(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/元素表.xlsx', sheet_name=None)
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
        combined_df = df.map(lambda x: None if pd.isna(x) else x)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('UI元素表',))
        return combined_df

    def ui_test_case(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/UI测试用例.xlsx', sheet_name=None)
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '用例名称': 'name',
        })
        combined_df = df.map(lambda x: None if pd.isna(x) else x)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('UI测试用例',))
        return combined_df

    def other_test_case(self):
        df = self.cls(fr'{project_dir.root_path()}/sources/excel/其他类型测试用例.xlsx', sheet_name=None)
        df = df.rename(columns={
            'ID': 'id',
            '项目名称': 'project_name',
            '用例名称': 'name',
        })
        combined_df = df.map(lambda x: None if pd.isna(x) else x)
        duplicate_ids = combined_df[combined_df.duplicated(subset=['id'], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=('其他测试用例',))
        return combined_df

    def cls(self, file_path: str, sheet_name=None):
        """
        读取Excel文件
        如果sheet_name为None，则读取所有sheet并合并
        如果指定sheet_name，则只读取指定sheet
        """
        if sheet_name is None:
            # 读取所有sheet
            excel_data = pd.read_excel(file_path, sheet_name=None)

            # 合并所有sheet的数据
            all_sheets_data = []
            for sheet_name, df in excel_data.items():
                # 添加sheet_name列标识来源
                df_copy = df.copy()
                df_copy['sheet_name'] = sheet_name
                all_sheets_data.append(df_copy)

            # 合并所有sheet
            if all_sheets_data:
                combined_data = pd.concat(all_sheets_data, ignore_index=True)
                return combined_data
            else:
                return pd.DataFrame()  # 返回空DataFrame

        else:
            # 读取指定sheet
            return pd.read_excel(file_path, sheet_name=sheet_name)


if __name__ == '__main__':
    print(ExcelData().api_test_case())
