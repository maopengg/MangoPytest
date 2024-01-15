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


class NoLoginAPI(DataProcessor, RequestTool):
    data_model: AIGCDataModel = AIGCDataModel()
    headers = {
        'Authorization': 'Bearer null',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'UserId': '121'
    }

    @classmethod
    @around(40)
    def no_login36(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(39)
    def no_login35(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(38)
    def no_login34(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(37)
    def no_login33(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(36)
    def no_login32(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(35)
    def no_login31(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(34)
    def no_login30(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(33)
    def no_login29(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(32)
    def no_login28(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(31)
    def no_login27(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(29)
    def no_login26(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(28)
    def no_login25(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(27)
    def no_login24(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(26)
    def no_login23(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(25)
    def no_login22(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.api_upload2(data, '关键词-auto_aigc-20230920.xlsx')

    @classmethod
    @around(24)
    def no_login21(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(23)
    def no_login20(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(22)
    def no_login19(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.api_upload2(data, '信息流-wuqiang-20230920.xlsx')

    @classmethod
    @around(21)
    def no_login18(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(20)
    def no_login17(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(19)
    def no_login16(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(18)
    def no_login15(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(17)
    def no_login14(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(16)
    def no_login13(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(15)
    def no_login12(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(14)
    def no_login11(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(13)
    def no_login10(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(12)
    def no_login9(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(11)
    def no_login8(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(10)
    def no_login7(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(9)
    def no_login6(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(8)
    def no_login5(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(6)
    def no_login4(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(5)
    def no_login3(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(4)
    def no_login2(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    @around(3)
    def no_login1(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        return cls.no_login(data)

    @classmethod
    def no_login(cls, data: ApiDataModel) -> ApiDataModel:
        """
        登录接口
        :return:
        """
        group = data.requests_list[data.step]
        group.request.url = f'{cls.data_model.host}{group.api_data.url}'
        group.request.headers = cls.headers
        return cls.http_request(data)

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
        group.request.headers = cls.headers
        group.request.headers.pop('Content-Type')
        group.request.file = files
        response = cls.http_request(data)
        return response


if __name__ == '__main__':
    print('ok')
