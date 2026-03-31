# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder fixtures 模块
# @Time   : 2026-03-31
# @Author : 毛鹏

# 认证模块 fixtures
from .auth_fixtures import (
    auth_builder,
    test_token,
    registered_user,
)

# 用户模块 fixtures
from .user_fixtures import (
    user_builder,
    test_user,
    new_user,
)

# 产品模块 fixtures
from .product_fixtures import (
    product_builder,
    test_product,
    product_list,
)

# 订单模块 fixtures
from .order_fixtures import (
    order_builder,
    test_order,
    order_with_product,
)

# 数据模块 fixtures
from .data_fixtures import (
    data_builder,
    submitted_data,
)

# 文件模块 fixtures
from .file_fixtures import (
    file_builder,
    temp_file,
    uploaded_file,
)

# 系统模块 fixtures
from .system_fixtures import (
    system_builder,
    server_health,
    server_info,
)

__all__ = [
    # 认证
    'auth_builder',
    'test_token',
    'registered_user',
    # 用户
    'user_builder',
    'test_user',
    'new_user',
    # 产品
    'product_builder',
    'test_product',
    'product_list',
    # 订单
    'order_builder',
    'test_order',
    'order_with_product',
    # 数据
    'data_builder',
    'submitted_data',
    # 文件
    'file_builder',
    'temp_file',
    'uploaded_file',
    # 系统
    'system_builder',
    'server_health',
    'server_info',
]
