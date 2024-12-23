# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-09-13 10:27
# @Author : 毛鹏

from models.api_model import ApiDataModel
from tools.assertion import Assertion
from tools.log import log

class CaseTool(Assertion):

    def case_run_mian(self, func, data: ApiDataModel) -> ApiDataModel:
        """
        公共请求方法
        @param func: 接口函数
        @param data: ApiDataModel
        @return: 响应结果
        """
        res: ApiDataModel = func(data=data)
        return res

    def ass_main(self, data: ApiDataModel) -> ApiDataModel:
        if data.test_case.ass_response_whole:
            log.debug(f'准备开始全匹配断言，断言数据：{data.test_case.ass_response_whole}')
            self.ass_response_whole(data.response.response_dict, data.test_case.ass_response_whole)
        return data
