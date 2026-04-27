# -*- coding: utf-8 -*-
"""
认证 Spec - 登录会话数据工厂 - pytest-factoryboy
"""

import factory
from pytest_factoryboy import register
from datetime import datetime, timedelta

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.entities.auth import AuthEntity
from auto_tests.bdd_api_mock.factories.specs.user import UserSpec


@register
class AuthSpec(BaseFactory):
    """认证会话 Spec"""

    class Meta:
        model = AuthEntity
        exclude = ("_user",)

    # 关联用户
    _user = factory.SubFactory(UserSpec)

    # 基础字段
    user_id = factory.SelfAttribute("_user.id")
    username = factory.SelfAttribute("_user.username")
    token = factory.Sequence(
        lambda n: f"AUTO-token-{n:06d}-{factory.Faker('uuid4').generate()}"
    )
    role = factory.SelfAttribute("_user.role")
    expires_at = factory.LazyAttribute(lambda _: datetime.now() + timedelta(hours=24))

    # Trait: 管理员会话
    class Params:
        admin = factory.Trait(role="admin")
        expired = factory.Trait(
            expires_at=factory.LazyAttribute(
                lambda _: datetime.now() - timedelta(hours=1)
            )
        )
