# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-04-02 9:48
# @Author : 毛鹏

from pandas.core.frame import DataFrame

from enums.tools_enum import SourcesTypeEnum
from exceptions.error_msg import ERROR_MSG_0347, ERROR_MSG_0348, ERROR_MSG_0349
from exceptions.tools_exception import GetProjectDataError, DataFrameQueryNullError, DataFrameQueryManyError
from settings.settings import SOURCES_TYPE
from sources.document_data.document_data import DocumentData
from sources.sql_data.sql_data import SqlData


class SourcesData:
    project: DataFrame = None
    notice_config: DataFrame = None
    test_object: DataFrame = None
    api_info: DataFrame = None
    api_test_case: DataFrame = None
    ui_element: DataFrame = None

    if SOURCES_TYPE == SourcesTypeEnum.SQL:
        r = SqlData()
        project = r.project()
        test_object = r.test_object()
        notice_config = r.notice_config()
        api_info = r.api_info()
        api_test_case = r.api_test_case()
        ui_element = r.ui_element()
    else:
        try:
            r = DocumentData()
            project = r.project()
            test_object = r.test_object()
            notice_config = r.notice_config()
            api_info = r.api_info()
            api_test_case = r.api_test_case()
            ui_element = r.ui_element()
        except AssertionError:
            raise GetProjectDataError(*ERROR_MSG_0347)

    @classmethod
    def get_test_object(cls, is_dict=True, **kwargs):
        return cls.get(cls.test_object, is_dict, **kwargs)

    @classmethod
    def get_project(cls, is_dict=True, **kwargs):
        return cls.get(cls.project, is_dict, **kwargs)

    @classmethod
    def get_notice_config(cls, is_dict=True, **kwargs):
        return cls.get(cls.notice_config, is_dict, **kwargs)

    @classmethod
    def get_api_info(cls, is_dict=True, **kwargs):
        return cls.get(cls.api_info, is_dict, **kwargs)

    @classmethod
    def get_api_test_case(cls, is_dict=True, **kwargs):
        return cls.get(cls.api_test_case, is_dict, **kwargs)

    @classmethod
    def get_ui_element(cls, is_dict=True, **kwargs):
        return cls.get(cls.ui_element, is_dict, **kwargs)

    @classmethod
    def get(cls, df: DataFrame, is_dict: bool, **kwargs) -> list[dict] | dict | None:
        conditions = None
        for key, value in kwargs.items():
            if conditions is None:
                conditions = (df[key] == value)
            else:
                conditions = conditions & (df[key] == value)
        result = df[conditions]
        if result.empty:
            raise DataFrameQueryNullError(*ERROR_MSG_0349, value=(str(kwargs), ))
        elif len(result) == 1:
            data = result.squeeze().to_dict()
        else:
            data = result.to_dict(orient='records')
        if is_dict:
            if isinstance(data, list):
                raise DataFrameQueryManyError(*ERROR_MSG_0348, value=(str(kwargs), ))
        return data


if __name__ == '__main__':
    print(SourcesData.project)
    print(SourcesData.test_object)
