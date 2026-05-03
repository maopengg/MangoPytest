# -*- coding: utf-8 -*-
"""
Steps 步骤定义层

提供 BDD 测试的步骤定义，按功能分类：

- common: 通用 fixtures
- api: API 请求步骤
- auth: 认证相关步骤
- data: 数据准备步骤
- assertions: 断言验证步骤
"""

# 导出 common fixtures
from auto_tests.bdd_api_mock.fixtures.bdd import api_response, created_entity

# 导出 API 请求步骤
from auto_tests.bdd_api_mock.steps.api import (
    api_get_step,
    api_get_with_params_step,
    api_get_with_table_params_step,
    api_post_step,
    api_put_step,
    api_delete_step,
    api_get_with_entity_step,
    api_post_with_entity_step,
    api_put_with_entity_step,
    api_delete_with_entity_step,
)

# 导出认证步骤
from auto_tests.bdd_api_mock.steps.auth import (
    user_logged_in_step,
    admin_logged_in_step,
    manager_logged_in_step,
    finance_logged_in_step,
    ceo_logged_in_step,
    user_login_step,
    login_should_succeed,
    login_should_fail,
    should_return_error_code,
)

# 导出数据准备步骤
from auto_tests.bdd_api_mock.steps.data import (
    create_entity_step,
    create_entity_step_with_prefix,
    create_entity_step_simple,
    create_entity_step_simple_with_prefix,
    create_multiple_entities_step,
    verify_entity_in_db,
)

# 导出断言步骤
from auto_tests.bdd_api_mock.steps.assertions import (
    response_code_should_be,
    response_code_should_be_cn,
    response_message_should_be,
    response_message_should_be_cn,
    response_message_should_contain,
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
    # Fixtures
    "api_response",
    "created_entity",
    # API 基础步骤
    "api_get_step",
    "api_get_with_params_step",
    "api_get_with_table_params_step",
    "api_post_step",
    "api_put_step",
    "api_delete_step",
    # API 实体步骤
    "api_get_with_entity_step",
    "api_post_with_entity_step",
    "api_put_with_entity_step",
    "api_delete_with_entity_step",
    # 认证步骤
    "user_logged_in_step",
    "admin_logged_in_step",
    "manager_logged_in_step",
    "finance_logged_in_step",
    "ceo_logged_in_step",
    "user_login_step",
    "login_should_succeed",
    "login_should_fail",
    "should_return_error_code",
    # 数据步骤
    "create_entity_step",
    "create_entity_step_with_prefix",
    "create_entity_step_simple",
    "create_entity_step_simple_with_prefix",
    "create_multiple_entities_step",
    "verify_entity_in_db",
    # 断言步骤
    "response_code_should_be",
    "response_code_should_be_cn",
    "response_message_should_be",
    "response_message_should_be_cn",
    "response_message_should_contain",
    "response_data_should_contain_field",
    "response_data_should_contain_field_cn",
    "response_data_field_should_be",
    "response_data_field_should_be_cn",
    "response_data_should_be_list",
    "response_data_should_be_list_cn",
    "response_data_list_length_should_be",
    "response_data_list_length_should_be_cn",
    "response_data_list_length_should_be_gte_cn",
    "db_should_contain_entity_simple",
]
