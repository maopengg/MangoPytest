# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据工厂模块 - 统一的数据管理入口
# @Time   : 2026-03-31
# @Author : 毛鹏

from typing import Dict, Any, Optional, Type

# 导出基础组件
from .base import DataFactoryBase
from .registry import BuilderRegistry, register_builder
from .sequences import SequenceGenerator
from .validators import DataValidator, ValidationError, CommonValidators

# 导出构造器
from .builders.base_builder import BaseBuilder
from .builders.d_module.user_builder import UserBuilder
from .builders.c_module.product_builder import ProductBuilder
from .builders.b_module.order_builder import OrderBuilder
from .builders.a_module.data_builder import DataBuilder
from .builders.a_module.system_builder import SystemBuilder

# 导出场景
from .scenarios import (
    BaseScenario,
    SimpleOrderScenario,
    BatchOrderScenario,
    ComplexWorkflowScenario
)


class DataFactory(DataFactoryBase):
    """
    数据工厂主类
    提供统一的数据创建、管理和清理接口

    使用示例：
        from auto_test.demo_project.data_factory import data_factory

        # 登录获取token
        data_factory.login()

        # 使用构造器创建数据
        user = data_factory.user.create()
        product = data_factory.product.create()
        order = data_factory.order.create(product_id=product['id'], user_id=user['id'])

        # 或使用预组装场景
        with data_factory.scenario_simple() as scenario:
            data = scenario.setup()
            # 执行测试...

        # 清理所有数据
        data_factory.cleanup_all()
    """

    def __init__(self):
        super().__init__()
        self._init_builders()
        self._init_scenarios()

    def _init_builders(self):
        """初始化构造器实例"""
        self._user_builder: Optional[UserBuilder] = None
        self._product_builder: Optional[ProductBuilder] = None
        self._order_builder: Optional[OrderBuilder] = None
        self._data_builder: Optional[DataBuilder] = None
        self._system_builder: Optional[SystemBuilder] = None

    def _init_scenarios(self):
        """初始化场景实例"""
        self._simple_scenario: Optional[SimpleOrderScenario] = None
        self._batch_scenario: Optional[BatchOrderScenario] = None
        self._complex_scenario: Optional[ComplexWorkflowScenario] = None

    def login(self, username: str = "testuser",
              password: str = "482c811da5d5b4bc6d497ffa98491e38") -> str:
        """
        用户登录，获取token
        @param username: 用户名
        @param password: 密码
        @return: token
        """
        # 使用user_builder进行登录
        if self._user_builder is None:
            self._user_builder = UserBuilder(factory=self)

        token = self._user_builder.login(username, password)
        if token:
            self.token = token
            # 更新所有builder的token
            self._update_builders_token(token)
        return token

    def _update_builders_token(self, token: str):
        """更新所有构造器的token"""
        builders = [
            self._user_builder,
            self._product_builder,
            self._order_builder,
            self._data_builder,
            self._system_builder
        ]
        for builder in builders:
            if builder:
                builder.set_token(token)

    @property
    def user(self) -> UserBuilder:
        """用户构造器"""
        if self._user_builder is None:
            self._user_builder = UserBuilder(self.token, self)
        return self._user_builder

    @property
    def product(self) -> ProductBuilder:
        """产品构造器"""
        if self._product_builder is None:
            self._product_builder = ProductBuilder(self.token, self)
        return self._product_builder

    @property
    def order(self) -> OrderBuilder:
        """订单构造器"""
        if self._order_builder is None:
            self._order_builder = OrderBuilder(self.token, self)
        return self._order_builder

    @property
    def data(self) -> DataBuilder:
        """数据构造器"""
        if self._data_builder is None:
            self._data_builder = DataBuilder(self.token, self)
        return self._data_builder

    @property
    def system(self) -> SystemBuilder:
        """系统构造器"""
        if self._system_builder is None:
            self._system_builder = SystemBuilder(self.token, self)
        return self._system_builder

    # ========== 场景快捷方法 ==========

    def scenario_simple(self) -> SimpleOrderScenario:
        """简单订单场景"""
        if self._simple_scenario is None:
            self._simple_scenario = SimpleOrderScenario(self)
        return self._simple_scenario

    def scenario_batch(self) -> BatchOrderScenario:
        """批量订单场景"""
        if self._batch_scenario is None:
            self._batch_scenario = BatchOrderScenario(self)
        return self._batch_scenario

    def scenario_complex(self) -> ComplexWorkflowScenario:
        """复杂工作流场景"""
        if self._complex_scenario is None:
            self._complex_scenario = ComplexWorkflowScenario(self)
        return self._complex_scenario

    # ========== 数据清理 ==========

    def cleanup_all(self):
        """清理所有创建的数据"""
        # 按依赖顺序清理：订单 -> 产品 -> 用户
        if self._order_builder:
            self._order_builder.cleanup()

        if self._product_builder:
            self._product_builder.cleanup()

        if self._user_builder:
            self._user_builder.cleanup()

        # 清空记录
        self.created_data.clear()
        self.clear_context()

    def cleanup_by_type(self, data_type: str):
        """
        按类型清理数据
        @param data_type: 数据类型 (user, product, order)
        """
        builder_map = {
            'user': self._user_builder,
            'product': self._product_builder,
            'order': self._order_builder
        }

        builder = builder_map.get(data_type)
        if builder:
            builder.cleanup()

        if data_type in self.created_data:
            del self.created_data[data_type]

    # ========== 工具方法 ==========

    def get_builder(self, name: str) -> BaseBuilder:
        """
        通过注册中心获取构造器
        @param name: 构造器名称
        @return: 构造器实例
        """
        return BuilderRegistry.create(name, token=self.token, factory=self)

    def health_check(self) -> bool:
        """检查服务健康状态"""
        return self.system.is_healthy()


# 数据工厂实例
data_factory = DataFactory()

__all__ = [
    # 主类
    'DataFactory',
    'data_factory',

    # 基础组件
    'DataFactoryBase',
    'BuilderRegistry',
    'register_builder',
    'SequenceGenerator',
    'DataValidator',
    'ValidationError',
    'CommonValidators',

    # 构造器
    'BaseBuilder',
    'UserBuilder',
    'ProductBuilder',
    'OrderBuilder',
    'DataBuilder',
    'SystemBuilder',

    # 场景
    'BaseScenario',
    'SimpleOrderScenario',
    'BatchOrderScenario',
    'ComplexWorkflowScenario',
]
