# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-13 10:27
# @Author : 毛鹏
import json

import allure

from models.api_model import ApiDataModel
from tools.assertion import Assertion
from tools.decorator.response import log_decorator


class CaseTool(Assertion):

    @log_decorator
    def case_run(self, func, data: ApiDataModel) -> ApiDataModel:
        """
        公共请求方法
        @param func: 接口函数
        @param data: ApiDataModel
        @return: 响应结果
        """
        res: ApiDataModel = func(data=data)
        self.assertion(res)
        return res

    def assertion(self, data: ApiDataModel):
        allure.attach(str(json.dumps(data.response.response_dict, ensure_ascii=False)), '断言-实际值')
        allure.attach(str(json.dumps(data.test_case.ass_response_whole, ensure_ascii=False)), '断言-期望值')
        if data.test_case.ass_response_whole:
            self.ass_response_whole(data.response.response_dict, data.test_case.ass_response_whole)
