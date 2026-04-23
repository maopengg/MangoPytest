# -*- coding: utf-8 -*-
"""
API 请求步骤

提供 HTTP 请求相关的步骤定义
"""

from auto_tests.bdd_api_mock.steps.api.base import (
    api_get_step,
    api_get_with_params_step,
    api_get_with_table_params_step,
    api_post_step,
    api_put_step,
    api_delete_step,
)
from auto_tests.bdd_api_mock.steps.api.entity import (
    api_get_with_entity_step,
    api_post_with_entity_step,
    api_put_with_entity_step,
    api_delete_with_entity_step,
)

__all__ = [
    "api_get_step",
    "api_get_with_params_step",
    "api_get_with_table_params_step",
    "api_post_step",
    "api_put_step",
    "api_delete_step",
    "api_get_with_entity_step",
    "api_post_with_entity_step",
    "api_put_with_entity_step",
    "api_delete_with_entity_step",
]
