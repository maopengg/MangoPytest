# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-04-02 9:48
# @Author : 毛鹏

from enums.tools_enum import SourcesTypeEnum
from exceptions.error_msg import ERROR_MSG_0347
from exceptions.tools_exception import GetProjectDataError
from settings.settings import SOURCES_TYPE
from sources.document_data.document_data import DocumentData
from sources.sql_data.sql_data import SqlData
from pandas.core.frame import DataFrame


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


if __name__ == '__main__':
    print(SourcesData.project)
    print(SourcesData.test_object)
    print(SourcesData.notice_config)
    print(SourcesData.api_info)
    print(SourcesData.api_test_case)
    print(SourcesData.ui_element)
    result = SourcesData.project[(SourcesData.project['id'] == 5) & (SourcesData.project['name'] == 'BaiduTranslate')]
    print(type(result))
    for index, row in result.iterrows():
        print(row['id'], row['name'])
    data = result['name']
    print(data.values[0])
    result_dict = result.to_dict(orient='records')
    print(result_dict)
