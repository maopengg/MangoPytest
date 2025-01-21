# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-09-13 10:27
# @Author : 毛鹏
import os

from mangokit import requests
from requests import RequestException

from models.api_model import ApiDataModel
from tools import project_dir
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
            log.debug(f'准备开始全匹配断言，预期值：{data.test_case.ass_response_whole}，实际值：{data.response.response_dict}')
            self.ass_response_whole(data.response.response_dict, data.test_case.ass_response_whole)
        return data

    def set_admin_headers(self, data: ApiDataModel, headers_type: str = 'admin'):
        for i in self.data_model.headers:
            if i.get('type') == headers_type:
                data.base_data.headers = i.get('headers')

    def save_file(self, file_name: str, data: ApiDataModel) -> str:
        file_path = os.path.join(project_dir.download(), file_name)
        if data.response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(data.response.content)
        else:
            assert False, f"下载失败，状态码: {data.response.status_code}"
        return file_path

    def save_file_by_url(self, url: str):
        file_name = url.split("/")[-1]
        file_path = os.path.join(project_dir.download(), file_name)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            else:
                assert False, f"下载失败，状态码: {response.status_code}"
        except RequestException as e:
            assert False, f"下载过程中出现异常: {e}"
