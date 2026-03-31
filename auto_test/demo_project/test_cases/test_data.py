# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据提交测试用例 - /api/data
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
import allure

from auto_test.demo_project.data_factory.builders.data import DataBuilder
from auto_test.demo_project.fixtures.conftest import *


@allure.feature("数据管理")
@allure.story("数据提交")
class TestSubmitData:
    """数据提交接口测试"""

    @allure.title("正常提交数据")
    def test_submit_data_success(self, test_token):
        """测试正常提交数据"""
        data_builder = DataBuilder(token=test_token)
        result = data_builder.submit(name="test_metric", value=100)
        
        assert result is not None
        assert result.get('name') == "test_metric"
        assert result.get('value') == 100
        assert 'timestamp' in result

    @allure.title("提交数据-使用fixture")
    def test_submit_data_with_fixture(self, submitted_data):
        """测试使用fixture提交的数据"""
        assert submitted_data is not None
        assert submitted_data.get('name') == "test_data"
        assert submitted_data.get('value') == 100
        assert 'timestamp' in submitted_data

    @allure.title("提交数据-不同数值")
    def test_submit_data_different_values(self, test_token):
        """测试提交不同数值的数据"""
        data_builder = DataBuilder(token=test_token)
        
        # 提交0
        result1 = data_builder.submit(name="zero_value", value=0)
        assert result1 is not None
        assert result1.get('value') == 0
        
        # 提交大数值
        result2 = data_builder.submit(name="large_value", value=999999)
        assert result2 is not None
        assert result2.get('value') == 999999
        
        # 提交负数值
        result3 = data_builder.submit(name="negative_value", value=-100)
        assert result3 is not None
        assert result3.get('value') == -100

    @allure.title("提交数据-特殊名称")
    def test_submit_data_special_names(self, test_token):
        """测试提交特殊名称的数据"""
        data_builder = DataBuilder(token=test_token)
        
        # 中文名称
        result1 = data_builder.submit(name="中文名称", value=100)
        assert result1 is not None
        
        # 包含空格
        result2 = data_builder.submit(name="name with spaces", value=200)
        assert result2 is not None
        
        # 包含特殊字符
        result3 = data_builder.submit(name="name_with-special.chars", value=300)
        assert result3 is not None

    @allure.title("提交数据失败-空name")
    def test_submit_data_empty_name(self, test_token):
        """测试提交空name的数据"""
        data_builder = DataBuilder(token=test_token)
        result = data_builder.submit(name="", value=100)
        
        assert result is None

    @allure.title("提交数据失败-空value")
    def test_submit_data_empty_value(self, test_token):
        """测试提交空value的数据"""
        data_builder = DataBuilder(token=test_token)
        result = data_builder.submit(name="test", value=None)
        
        # 根据mock_api的实现，None会被转为空字符串，导致失败
        assert result is None

    @allure.title("提交数据失败-非数字value")
    def test_submit_data_non_numeric_value(self, test_token):
        """测试提交非数字value的数据"""
        data_builder = DataBuilder(token=test_token)
        
        # 提交字符串数值
        api_data = data_builder._create_api_data(
            url="/api/data",
            method="POST",
            json_data={"name": "test", "value": "not_a_number"}
        )
        result = data_builder.http(api_data)
        
        # 应该返回错误
        assert result.response is not None
        response_json = result.response.json()
        assert response_json.get('code') != 200
