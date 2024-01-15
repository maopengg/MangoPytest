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


class AccountAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(8)
    def api_account_exists(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(9)
    def api_account_list(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(10)
    def api_account_init_account(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(11)
    def api_brands_check(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(12)
    def api_brands_add(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(13)
    def api_brands_list(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        return cls.http(data)

    @classmethod
    @around(14)
    def api_brands_update(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        sql = f'select a.id as id from brands a inner join sys_user b on a.user_id=b.user_id where b.user_name="auto_aigc" and a.account_name="OLAY" and a.`status`=0 and a.`status`=0;'
        query: dict = cls.data_model.mysql_obj.execute_query(sql)[0]
        data.test_case_data.case_json['id'] = query.get("id")
        return cls.http(data)

    @classmethod
    @around(14)
    def api_brands_update2(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        sql = f'select a.id as id from brands a inner join sys_user b on a.user_id=b.user_id where b.user_name="auto_aigc" and a.account_name="测试品牌"and a.`status`=0 and a.`status`=0;'
        query: dict = cls.data_model.mysql_obj.execute_query(sql)[0]
        data.test_case_data.case_json['id'] = query.get("id")
        return cls.http(data)

    @classmethod
    @around(15)
    def api_brands_delete(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询账户是否存在
        :return: 响应结果，请求url，请求头
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'

        # 此处需要检查什么时候传递值进入 group.request.params
        if data.test_case_data.case_params is None or len(data.test_case_data.case_params) == 0:
            sql = f'select a.id as id from brands a inner join sys_user b on a.user_id=b.user_id where b.user_name="auto_aigc" and a.account_name="OLAY" and a.`status`=0 and b.`status`=0 ;'
            query: dict = cls.data_model.mysql_obj.execute_query(sql)[0]
            group.request.params = query
        return cls.http_request(data)


if __name__ == '__main__':
    pass
