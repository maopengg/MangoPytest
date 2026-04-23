# -*- coding: utf-8 -*-
"""
断言验证步骤

提供响应状态码、消息、数据字段等验证步骤
"""

from auto_tests.bdd_api_mock.steps.assertions.response import (
    response_code_should_be,
    response_code_should_be_cn,
    response_message_should_be,
    response_message_should_be_cn,
    response_message_should_contain,
)
from auto_tests.bdd_api_mock.steps.assertions.data import (
    response_data_should_contain_field,
    response_data_should_contain_field_cn,
    response_data_field_should_be,
    response_data_field_should_be_cn,
    response_data_should_be_list,
    response_data_should_be_list_cn,
    response_data_list_length_should_be,
    response_data_list_length_should_be_cn,
    response_data_list_length_should_be_gte_cn,
    db_should_contain_entity_simple,
)

__all__ = [
    # 响应状态码断言
    "response_code_should_be",
    "response_code_should_be_cn",
    # 响应消息断言
    "response_message_should_be",
    "response_message_should_be_cn",
    "response_message_should_contain",
    # 响应数据断言
    "response_data_should_contain_field",
    "response_data_should_contain_field_cn",
    "response_data_field_should_be",
    "response_data_field_should_be_cn",
    # 列表断言
    "response_data_should_be_list",
    "response_data_should_be_list_cn",
    "response_data_list_length_should_be",
    "response_data_list_length_should_be_cn",
    "response_data_list_length_should_be_gte_cn",
    # 数据库断言
    "db_should_contain_entity_simple",
]
