# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏

from models.api_model import ApiDataModel
from models.models import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class CreatingTemplatesAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(32)
    def api_xhs_check(cls, data: ApiDataModel) -> ApiDataModel:
        """
        小红书每日报告list
        :return: 响应结果，请求url，请求头
        """
        if data.db_is_ass:
            # 数据库查询数据，重置断言
            account_id = data.test_case_data.case_params.get("accountId")
            date = data.test_case_data.case_params.get("date")
            sql_unit_counts = f'select COUNT(1) as unitCounts from info_flow_table where date="{date}" and account_id="{account_id}"'
            sql_unit = f'select COUNT(1) as unit from unit_data where account_id="{account_id}" and `status`=0'
            sql_key_words_counts = f'select COUNT(1) as keyWordsCounts from search_keyword_table where date="{date}" and account_id="{account_id}"'
            sql_key_words = f'select COUNT(1) as keyword from keyword_data where account_id="{account_id}" and `status`=0'
            sql_unit_counts_query: dict = cls.data_model.mysql_obj.execute_query(sql_unit_counts)[0]
            sql_unit_query: dict = cls.data_model.mysql_obj.execute_query(sql_unit)[0]
            sql_key_words_counts_query: dict = cls.data_model.mysql_obj.execute_query(sql_key_words_counts)[0]
            sql_key_words_query: dict = cls.data_model.mysql_obj.execute_query(sql_key_words)[0]
            data.test_case_data.case_ass['data']['unit'] = sql_unit_query['unit']
            data.test_case_data.case_ass['data']['unitCount'] = sql_unit_counts_query['unitCounts']
            data.test_case_data.case_ass['data']['keyword'] = sql_key_words_query['keyword']
            data.test_case_data.case_ass['data']['keywordCount'] = sql_key_words_counts_query['keyWordsCounts']
        return cls.http(data)

    @classmethod
    @around(37)
    def api_xhs_get(cls, data: ApiDataModel) -> ApiDataModel:
        """
        小红书每日报告list
        :return: 响应结果，请求url，请求头
        """

        return cls.http(data)

    @classmethod
    @around(35)
    def api_ai_generateDaily(cls, data: ApiDataModel) -> ApiDataModel:
        """
        小红书每日报告list
        :return: 响应结果，请求url，请求头
        """
        data.test_case_data.case_json['request_id'] = cls.random_str(12)
        return cls.http(data)


if __name__ == '__main__':
    pass
