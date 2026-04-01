# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景基类 - 业务流程封装
# @Time   : 2026-03-31
# @Author : 毛鹏
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic
from dataclasses import dataclass, field

from ..entities.base_entity import BaseEntity


T = TypeVar("T", bound=BaseEntity)


@dataclass
class ScenarioResult:
    """场景执行结果"""

    success: bool = True
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    entities: Dict[str, BaseEntity] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def add_entity(self, name: str, entity: BaseEntity):
        """添加实体到结果"""
        self.entities[name] = entity

    def get_entity(self, name: str) -> Optional[BaseEntity]:
        """获取实体"""
        return self.entities.get(name)

    def add_error(self, error: str):
        """添加错误信息"""
        self.success = False
        self.errors.append(error)
        self.message = error if not self.message else f"{self.message}; {error}"


class BaseScenario(ABC, Generic[T]):
    """
    场景基类

    职责：
    1. 封装业务流程（多个步骤的组合）
    2. 管理实体间的依赖关系
    3. 提供场景执行结果

    使用示例：
        class LoginScenario(BaseScenario):
            def execute(self, username: str, password: str) -> ScenarioResult:
                # 1. 创建用户实体
                user = UserEntity(...)
                # 2. 执行登录
                # 3. 返回结果
                pass
    """

    def __init__(self, token: str = None, factory=None):
        """
        初始化场景

        @param token: 认证token
        @param factory: 数据工厂实例
        """
        self.token = token
        self.factory = factory
        self._created_entities: List[BaseEntity] = []

    @abstractmethod
    def execute(self, *args, **kwargs) -> ScenarioResult:
        """
        执行场景

        子类必须实现此方法定义场景逻辑

        @return: 场景执行结果
        """
        pass

    def pre_execute(self, *args, **kwargs) -> bool:
        """
        执行前准备

        子类可重写此方法进行前置检查

        @return: 是否继续执行
        """
        return True

    def post_execute(self, result: ScenarioResult):
        """
        执行后处理

        子类可重写此方法进行后置处理

        @param result: 执行结果
        """
        pass

    def run(self, *args, **kwargs) -> ScenarioResult:
        """
        运行场景（完整生命周期）

        @return: 场景执行结果
        """
        # 前置检查
        if not self.pre_execute(*args, **kwargs):
            return ScenarioResult(success=False, message="前置检查失败")

        try:
            # 执行场景
            result = self.execute(*args, **kwargs)
        except Exception as e:
            result = ScenarioResult(success=False, message=f"场景执行异常: {str(e)}")

        # 后置处理
        self.post_execute(result)

        return result

    def register_entity(self, entity: BaseEntity):
        """
        注册创建的实体

        @param entity: 实体实例
        """
        self._created_entities.append(entity)

    def get_created_entities(self) -> List[BaseEntity]:
        """
        获取所有创建的实体

        @return: 实体列表
        """
        return self._created_entities.copy()

    def cleanup(self):
        """
        清理场景创建的数据

        子类可重写此方法自定义清理逻辑
        """
        # 默认清理所有注册的实体
        for entity in reversed(self._created_entities):
            if hasattr(entity, "mark_as_deleted"):
                entity.mark_as_deleted()

        self._created_entities.clear()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
