# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
import copy

from config.get_path import ensure_path_sep
from models.api_model import ApiDataModel, CaseGroupModel
from models.models import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class DataMappingAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(20)
    def api_unit_list(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'

        response = cls.http(data)
        # where_str = cls.dict_to_sql_conditions(data.test_case_data.case_params).replace('kolNote', 'kol_note').replace(
        #    'unitName', 'unit_name').replace('deliveryWay', 'delivery_way').replace('brandName', 'brand_name')
        # sql_after = f'select COUNT(1) as counts from (select DISTINCT account_id,unit_name  from unit_data where account_id in (select DISTINCT account_id from brands where user_id=121 and `status`=0) {where_str}) as a;'
        # query: dict = cls.data_model.mysql_obj.execute_query(sql_after)[0]
        # result = len(group.response.response_json.get("data")["records"])
        # assert query["counts"] == result
        return response

    @classmethod
    @around(21)
    def api_unit_update(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(22)
    def api_unit_upload(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        # file_path = ensure_path_sep('/case_files/信息流-wuqiang-20230920.xlsx')
        # files = [
        #     ('file', ('信息流-wuqiang-20230920.xlsx', open(file_path, 'rb'),
        #               'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        # ]
        # group: CaseGroupModel = data.requests_list[data.step]
        # group.request.url = f'{cls.data_model.host}{group.api_data.url}'
        # headers = copy.deepcopy(cls.data_model.headers)
        # group.request.headers = headers
        # group.request.headers.pop('Content-Type')
        # group.request.file = files
        # response = cls.http_request(data)
        # return response

        return cls.api_upload2(data, '信息流-wuqiang-20230920.xlsx')

    @classmethod
    @around(22)
    def api_unit_upload2(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.api_upload2(data, '非法的文件.xlsx')

    @classmethod
    @around(23)
    def api_key_word_list(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'
        response = cls.http(data)
        return response

    @classmethod
    @around(24)
    def api_key_word_update(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(25)
    def api_key_word_upload(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.api_upload2(data, '关键词-auto_aigc-20230920.xlsx')

    @classmethod
    @around(25)
    def api_key_word_upload2(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.api_upload2(data, '非法的文件.xlsx')

    @classmethod
    def api_upload2(cls, data: ApiDataModel, file_name: str) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        file_path = ensure_path_sep('/case_files/' + file_name)
        files = [
            ('file', (file_name, open(file_path, 'rb'),
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
        ]
        group: CaseGroupModel = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'
        headers = copy.deepcopy(cls.data_model.headers)
        group.request.headers = headers
        group.request.headers.pop('Content-Type')
        group.request.file = files
        response = cls.http_request(data)
        return response

    @classmethod
    @around(33)
    def api_xhs_count(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        if data.db_is_ass:
            sql_unit = f'select COUNT(1) as unitCounts from unit_data  where   account_id in (select account_id from brands where `status`=0 and user_id=121)'
            sql_key_words = f'select COUNT(1) as keywordCounts from keyword_data  where   account_id in (select account_id from brands where `status`=0 and user_id=121)'
            sql_unit_query: dict = cls.data_model.mysql_obj.execute_query(sql_unit)[0]
            sql_key_words_query: dict = cls.data_model.mysql_obj.execute_query(sql_key_words)[0]
            data.test_case_data.case_ass['data']['unit'] = sql_unit_query['unitCounts']
            data.test_case_data.case_ass['data']['keyword'] = sql_key_words_query['keywordCounts']
        return cls.http(data)

    @classmethod
    @around(34)
    def api_xhs_download(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """

        response = cls.http(data)
        file_path = ensure_path_sep('/case_files/down_tmp/' + 'tmp.xlsx')
        cls.excel_write(response.requests_list[0].response.content, file_path)
        return response


if __name__ == '__main__':
    pass
