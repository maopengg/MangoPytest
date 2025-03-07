# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-03-17 19:50
# @Author : 毛鹏
from auto_test.api_wan_android import WanAndroidDataModel
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class CollectionAPI(RequestTool):
    data_model = WanAndroidDataModel()
    #获取用户收藏的文章列表
    @request_data(2)
    def api_list(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
    #收藏站内文章
    @request_data(15)
    def api_add_essay(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
    #修改文章
    @request_data(17)
    def api_seeay_update(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
    #取消文章收藏
    @request_data(18)
    def api_essay_uncollect(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    #收藏网站
    @request_data(19)
    def api_add_site(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
    #获取用户收藏的网站列表
    @request_data(20)
    def api_user_site(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
    #编辑收藏的网站
    @request_data(21)
    def api_update_site(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
    #删除收藏的网站
    @request_data(22)
    def api_delete_site(self, data: ApiDataModel) -> ApiDataModel:
        """
        发请求的函数
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)