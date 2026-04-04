# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API 测试用例工具类
# @Time   : 2023-09-13 10:27
# @Author : 毛鹏
"""
API 测试用例工具模块

提供 API 测试用例的通用功能：
- 用例执行
- 断言处理
- 文件下载

使用示例：
    from core.api import CaseTool
    
    case_tool = CaseTool()
    result = case_tool.case_run_mian(api_func, data)
    case_tool.ass_main(result)
"""
import os

import requests
from requests import RequestException

from models.api_model import ApiDataModel
from tools import project_dir
from tools.assertion import Assertion
from tools.log import log


class CaseTool(Assertion):
    """
    API 测试用例工具类
    
    封装 API 测试用例的通用功能
    """

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
        """
        主断言方法
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        if data.test_case.ass_response_whole:
            log.debug(
                f'准备开始全匹配断言，预期值：{data.test_case.ass_response_whole}，实际值：{data.response.response_dict}')
            self.ass_response_whole(data.response.response_dict, data.test_case.ass_response_whole)
        actual = data.response.response_dict
        expect = data.test_case.ass_schema
        if actual and expect:
            self.ass_schema(actual, expect)
        return data

    def set_admin_headers(self, data: ApiDataModel, headers_type: str = 'admin'):
        """
        设置管理员请求头
        @param data: ApiDataModel
        @param headers_type: 请求头类型
        """
        for i in self.data_model.headers:
            if i.get('type') == headers_type:
                data.base_data.headers = i.get('headers')

    def save_file(self, file_name: str, data: ApiDataModel) -> str:
        """
        保存响应文件
        @param file_name: 文件名
        @param data: ApiDataModel
        @return: 文件路径
        """
        file_path = os.path.join(project_dir.download(), file_name)
        if data.response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(data.response.content)
        else:
            assert False, f"下载失败，状态码: {data.response.status_code}"
        return file_path

    def save_file_by_url(self, url: str):
        """
        通过 URL 下载文件
        @param url: 文件 URL
        @return: 文件路径
        """
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
