# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2024-04-01 22:11
# @Author : 毛鹏
import pandas
from pandas.core.frame import DataFrame

from settings.settings import PROJECT, API_TEST_CASE, API_INFO, UI_ELEMENT
from tools.base_request.request_tool import RequestTool


class ProjectInfoApi:
    headers = {
        'Authorization': 'Bearer u-fzf1SbkTNfYVZgUUaRe.c9l00T4h40J3pG00hhG0819k',
        'Content-Type': 'application/json; charset=utf-8'
    }
    project: DataFrame = None
    notice_config: DataFrame = None
    test_object: DataFrame = None
    api_info: DataFrame = None
    api_test_case: DataFrame = None
    ui_element: DataFrame = None

    def __init__(self):
        self.url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/"
        self.parameter = "&valueRenderOption=ToString&dateTimeRenderOption=FormattedString"

    def main(self):
        self.base_info()
        self.api_info_base()
        self.api_test_case_base()
        self.ui_element_base()

    def base_info(self):
        for i in PROJECT[1]:
            if i.get('title') == '项目信息':
                url = f"{self.url}{PROJECT[0]}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
                self.project = self.cls(url)
            elif i.get('title') == '通知配置':
                url = f"{self.url}{PROJECT[0]}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
                self.notice_config = self.cls(url)
            elif i.get('title') == '测试环境':
                url = f"{self.url}{PROJECT[0]}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
                self.test_object = self.cls(url)

    def api_info_base(self):
        url = f"{self.url}{API_INFO[0]}/values_batch_get?ranges={API_INFO[1][0].get('sheet_id')}{self.parameter}"
        self.api_info = self.cls(url)

    def api_test_case_base(self):
        url = f"{self.url}{API_TEST_CASE[0]}/values_batch_get?ranges={API_TEST_CASE[1][0].get('sheet_id')}{self.parameter}"
        self.api_test_case = self.cls(url)

    def ui_element_base(self):
        url = f"{self.url}{UI_ELEMENT[0]}/values_batch_get?ranges={UI_ELEMENT[1][0].get('sheet_id')}{self.parameter}"
        self.ui_element = self.cls(url)

    @classmethod
    def cls(cls, url):
        response = RequestTool.internal_http(url, "GET", headers=cls.headers)
        response_dict = response.json()
        data = response_dict['data']['valueRanges'][0]['values']
        df = pandas.DataFrame(data, columns=data[0])
        df = df.drop(0)  # 删除第一行数据，因为它已经作为了列名
        return df.dropna(how='all')  # 清空全是null的
