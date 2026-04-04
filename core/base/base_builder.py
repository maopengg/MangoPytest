# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Builder基类 - 支持Strategy和自动依赖解决
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
Builder基类模块

新特性：
1. 集成Strategy层（支持API/DB/Hybrid/Mock）
2. 自动依赖解决（D→C→B→A级联构造）
3. 级联清理（可选）
4. 依赖注入（parent_builders）
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Type, Dict, Any

from .base_entity import BaseEntity
from .builder_context import BuilderContext

T = TypeVar("T", bound=BaseEntity)


def _get_default_strategy():
    """延迟导入默认策略，避免循环导入"""
    from auto_tests.demo_project.data_factory.strategies import APIStrategy

    return APIStrategy()


class BaseBuilder(ABC, Generic[T]):
    """
    Builder基类（增强版）

    新特性：
    1. 集成Strategy层（支持API/DB/Hybrid/Mock）
    2. 自动依赖解决（D→C→B→A级联构造）
    3. 级联清理（可选）
    4. 依赖注入（parent_builders）

    使用示例：
        # 基础用法
        builder = ReimbursementBuilder(
            token="xxx",
            context=BuilderContext(strategy=APIStrategy())
        )
        reimb = builder.create(user_id=1, amount=1000)

        # 自动依赖解决
        payment_builder = PaymentBuilder(
            token="xxx",
            context=BuilderContext(auto_prepare_deps=True)
        )
        # 自动创建报销单→预算→组织→用户
        payment = payment_builder.create(amount=5000)
    """

    # 依赖层级（子类重写）
    DEPENDENCY_LEVEL: Optional[Any] = None

    # 依赖的Builder类型（子类重写）
    # 例如：DEPENDENCIES = [ReimbursementBuilder, BudgetBuilder]
    DEPENDENCIES: List[Type["BaseBuilder"]] = []

    def __init__(
        self,
        token: Optional[str] = None,
        context: Optional[BuilderContext] = None,
        strategy: Optional[Any] = None,
        parent_builders: Optional[Dict[str, "BaseBuilder"]] = None,
        factory=None,
    ):
        """
        初始化Builder

        @param token: 认证token
        @param context: 执行上下文（追踪、清理、策略）
        @param strategy: 数据策略（覆盖context中的策略）
        @param parent_builders: 父Builder字典（依赖注入）
        @param factory: 数据工厂实例
        """
        self.token = token
        self.factory = factory

        # 初始化或复用上下文
        self.context = context or BuilderContext()

        # 策略优先级：传入的strategy > context.strategy > 默认APIStrategy
        if strategy:
            self.context.strategy = strategy
        elif self.context.strategy is None:
            # 使用默认的 API 策略（延迟导入避免循环）
            self.context.strategy = _get_default_strategy()

        # 父Builder（依赖注入）
        self._parent_builders = parent_builders or {}

        # 注册自己到上下文
        self.context.register_builder(self.__class__.__name__, self)

        # 初始化依赖Builder
        self._dep_builders: Dict[str, "BaseBuilder"] = {}
        self._init_dependency_builders()

    def _init_dependency_builders(self):
        """初始化依赖的Builder"""
        for dep_builder_class in self.DEPENDENCIES:
            builder_name = dep_builder_class.__name__

            # 优先使用注入的parent_builder
            if builder_name in self._parent_builders:
                self._dep_builders[builder_name] = self._parent_builders[builder_name]
            # 其次使用context中已注册的
            elif self.context.get_builder(builder_name):
                self._dep_builders[builder_name] = self.context.get_builder(
                    builder_name
                )
            # 否则创建新的（共享context）
            else:
                builder = dep_builder_class(
                    token=self.token,
                    context=self.context,  # 共享上下文
                    parent_builders=self._dep_builders,  # 传递已创建的依赖
                )
                self._dep_builders[builder_name] = builder
                self.context.register_builder(builder_name, builder)

    def _get_or_create_builder(
        self, builder_class: Type["BaseBuilder"]
    ) -> "BaseBuilder":
        """
        获取或创建依赖Builder

        @param builder_class: Builder类
        @return: Builder实例
        """
        builder_name = builder_class.__name__

        if builder_name not in self._dep_builders:
            self._dep_builders[builder_name] = builder_class(
                token=self.token,
                context=self.context,
                parent_builders=self._dep_builders,
            )
            self.context.register_builder(
                builder_name, self._dep_builders[builder_name]
            )

        return self._dep_builders[builder_name]

    @abstractmethod
    def build(self, **kwargs) -> T:
        """
        构造实体（不调用API）

        @param kwargs: 构造参数
        @return: 实体实例
        """
        pass

    @abstractmethod
    def create(
        self, entity: Optional[T] = None, auto_prepare_deps: bool = True, **kwargs
    ) -> Optional[T]:
        """
        创建实体（调用Strategy）

        @param entity: 预构造的实体（可选）
        @param auto_prepare_deps: 是否自动准备依赖数据
        @param kwargs: 创建参数
        @return: 创建后的实体（含ID）
        """
        pass

    def _prepare_dependencies(self, **kwargs) -> Dict[str, Any]:
        """
        准备依赖数据

        子类重写此方法实现自动依赖解决逻辑

        @param kwargs: 原始参数
        @return: 补充依赖后的参数
        """
        # 默认实现：直接返回原始参数
        # 子类应根据需要补充缺失的依赖
        return kwargs

    def _do_create(self, entity: T) -> Optional[T]:
        """
        执行创建（通过Strategy）

        @param entity: 实体实例
        @return: 创建后的实体
        """
        # 使用Strategy创建
        result = self.context.strategy.create(entity.__class__, **entity.__dict__)

        if result.success:
            created_entity = result.entity
            # 追踪
            self._register_created(created_entity)
            self.context.track(
                entity_type=created_entity.__class__.__name__,
                entity_id=getattr(created_entity, "id", None),
                builder=self,
            )
            return created_entity
        else:
            # 记录错误
            print(f"创建失败: {result.error_code} - {result.error_message}")
            return None

    def _register_created(self, entity: BaseEntity):
        """
        注册创建的实体（用于后续清理）

        @param entity: 实体实例
        """
        if entity and hasattr(entity, "id") and entity.id:
            # 添加到本地追踪列表
            if not hasattr(self, "_created_entities"):
                self._created_entities: List[BaseEntity] = []
            self._created_entities.append(entity)

    def cleanup(self):
        """
        清理创建的数据

        支持级联清理（如果context.cascade_cleanup为True）
        """
        # 清理本Builder创建的数据
        if hasattr(self, "_created_entities"):
            for entity in reversed(self._created_entities):
                try:
                    self._delete_entity(entity)
                except Exception as e:
                    print(f"清理失败: {e}")
            self._created_entities.clear()

        # 级联清理依赖（如果启用）
        if self.context.cascade_cleanup:
            for dep_builder in self._dep_builders.values():
                try:
                    dep_builder.cleanup()
                except Exception as e:
                    print(f"依赖清理失败: {e}")

    def _delete_entity(self, entity: BaseEntity):
        """
        删除单个实体（通过Strategy）

        @param entity: 要删除的实体
        """
        entity_id = getattr(entity, "id", None)
        if entity_id:
            self.context.strategy.delete(entity.__class__, entity_id)
        entity.mark_as_deleted()

    def get_created_entities(self) -> List[BaseEntity]:
        """
        获取所有创建的实体

        @return: 实体列表
        """
        if hasattr(self, "_created_entities"):
            return self._created_entities.copy()
        return []

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
