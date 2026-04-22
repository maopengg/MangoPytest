# -*- coding: utf-8 -*-
"""
用户 Spec - factory_boy
使用 AUTO_ 前缀，便于自动清理
"""

import factory
import hashlib
from datetime import datetime

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.factories.utils import auto_username
from auto_tests.bdd_api_mock.entities.user.user_entity import UserEntity


class UserSpec(BaseFactory):
    """用户 Spec"""

    class Meta:
        model = UserEntity

    # 基本字段 - 使用 AUTO_ 前缀
    username = factory.LazyFunction(lambda: auto_username("USER"))
    email = factory.LazyAttribute(lambda o: f"{o.username.lower()}@example.com")
    full_name = factory.LazyAttribute(lambda o: f"用户 {o.username}")
    password = factory.LazyFunction(
        lambda: hashlib.md5("password123".encode()).hexdigest()
    )
    role = "user"
    status = "active"
    last_login_at = None
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    # Trait: 不同角色
    class Params:
        is_admin = factory.Trait(
            role="admin", username=factory.LazyFunction(lambda: auto_username("ADMIN"))
        )
        is_manager = factory.Trait(
            role="manager",
            username=factory.LazyFunction(lambda: auto_username("MANAGER")),
        )
        is_finance = factory.Trait(
            role="finance",
            username=factory.LazyFunction(lambda: auto_username("FINANCE")),
        )
        is_ceo = factory.Trait(
            role="ceo", username=factory.LazyFunction(lambda: auto_username("CEO"))
        )
