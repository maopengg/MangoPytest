# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-04-23 11:23
# @Author : 毛鹏
from auto_test.api.mango_testing_platform import MangoDataModel
from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class IndexAPI(RequestTool):
    data_model = MangoDataModel()

    @request_data(5)
    def api_menu(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(6)
    def api_system_case_result_week_sum(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(7)
    def api_user_project_module_get_all(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(8)
    def api_user_project_all(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(9)
    def api_system_case_sum(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(10)
    def api_system_case_run_sum(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(11)
    def api_system_test_obj_name(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(12)
    def api_system_activity_level(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)

    @request_data(13)
    def api_system_socket_all_user_sum(self, data: ApiDataModel) -> ApiDataModel:
        return self.http(data)
