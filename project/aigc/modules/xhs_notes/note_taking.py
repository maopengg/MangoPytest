# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-18 11:31
# @Author : 毛鹏
from models.api_model import ApiDataModel, CaseGroupModel
from models.models import AIGCDataModel
from tools.data_processor import DataProcessor
from tools.decorator.response import around
from tools.request_tool.request_tool import RequestTool


class NoteTakingAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()

    @classmethod
    @around(26)
    def api_note_filter_dropdown_options(cls, data: ApiDataModel) -> ApiDataModel:
        """
        获取笔记筛选下拉选项
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return cls.http(data)

    @classmethod
    @around(27)
    def api_query_note_list(cls, data: ApiDataModel) -> ApiDataModel:
        """
        查询笔记列表
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return cls.http(data)

    @classmethod
    @around(28)
    def api_query_note_key(cls, data: ApiDataModel) -> ApiDataModel:
        """
        根据主键Id 获取笔记信息
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return cls.http(data)
