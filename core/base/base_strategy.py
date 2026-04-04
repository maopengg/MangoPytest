# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 策略基类
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
策略基类模块

定义数据构造和持久化的通用接口，所有具体策略必须实现这些方法。
"""

from abc import ABC, abstractmethod
from typing import Type, List, Optional, Dict, Any, TypeVar, Generic

from .strategy_result import StrategyResult

T = TypeVar("T", bound=Any)


class BaseStrategy(ABC, Generic[T]):
    """
    策略基类

    定义数据构造和持久化的通用接口，所有具体策略必须实现这些方法。

    职责：
    1. 实体创建/更新/删除的抽象接口
    2. 批量操作支持
    3. 事务管理（如支持）
    4. 错误处理统一封装

    使用示例：
        class MyStrategy(BaseStrategy[UserEntity]):
            def create(self, entity_type: Type[UserEntity], **kwargs) -> StrategyResult:
                # 实现创建逻辑
                pass
    """

    def __init__(self, context: Optional[Any] = None, config: Optional[Dict] = None):
        """
        初始化策略

        @param context: 执行上下文（用于追踪、清理等）
        @param config: 策略配置
        """
        self.context = context
        self.config = config or {}
        self._transaction_stack: List[Dict] = []

    @abstractmethod
    def create(self, entity_type: Type[T], **kwargs) -> StrategyResult:
        """
        创建实体

        @param entity_type: 实体类型
        @param kwargs: 实体属性
        @return: 策略执行结果
        """
        pass

    @abstractmethod
    def update(self, entity: T, **kwargs) -> StrategyResult:
        """
        更新实体

        @param entity: 实体实例
        @param kwargs: 更新属性
        @return: 策略执行结果
        """
        pass

    @abstractmethod
    def delete(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        删除实体

        @param entity_type: 实体类型
        @param entity_id: 实体ID
        @return: 策略执行结果
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        根据ID获取实体

        @param entity_type: 实体类型
        @param entity_id: 实体ID
        @return: 策略执行结果
        """
        pass

    def batch_create(self, entity_type: Type[T], data_list: List[Dict]) -> StrategyResult:
        """
        批量创建实体（默认实现为循环调用create）

        @param entity_type: 实体类型
        @param data_list: 数据列表
        @return: 策略执行结果
        """
        entities = []
        errors = []

        for idx, data in enumerate(data_list):
            result = self.create(entity_type, **data)
            if result.success:
                entities.append(result.entity)
            else:
                errors.append({"index": idx, "error": result.error_message})

        return StrategyResult(
            success=len(errors) == 0,
            entities=entities,
            metadata={"total": len(data_list), "success": len(entities), "failed": len(errors), "errors": errors}
        )

    def batch_delete(self, entity_type: Type[T], entity_ids: List[Any]) -> StrategyResult:
        """
        批量删除实体

        @param entity_type: 实体类型
        @param entity_ids: 实体ID列表
        @return: 策略执行结果
        """
        success_count = 0
        errors = []

        for idx, entity_id in enumerate(entity_ids):
            result = self.delete(entity_type, entity_id)
            if result.success:
                success_count += 1
            else:
                errors.append({"index": idx, "entity_id": entity_id, "error": result.error_message})

        return StrategyResult(
            success=len(errors) == 0,
            metadata={"total": len(entity_ids), "success": success_count, "failed": len(errors), "errors": errors}
        )

    def begin_transaction(self):
        """开始事务（如果策略支持）"""
        self._transaction_stack.append({"status": "started", "operations": []})

    def commit_transaction(self):
        """提交事务"""
        if self._transaction_stack:
            self._transaction_stack.pop()

    def rollback_transaction(self):
        """回滚事务"""
        # 子类可根据需要实现
        pass

    def _record_operation(self, operation: str, entity_type: Type, entity_id: Any):
        """
        记录操作（用于追踪和回滚）

        @param operation: 操作类型
        @param entity_type: 实体类型
        @param entity_id: 实体ID
        """
        if self._transaction_stack:
            self._transaction_stack[-1]["operations"].append({
                "operation": operation,
                "entity_type": entity_type.__name__,
                "entity_id": entity_id
            })

    def _track_entity(self, entity: Any, operation: str = "created"):
        """
        追踪实体（用于后续清理）

        @param entity: 实体实例
        @param operation: 操作类型
        """
        if self.context and hasattr(self.context, "track"):
            self.context.track(
                entity_type=entity.__class__.__name__,
                entity_id=getattr(entity, "id", None),
                source=self.__class__.__name__,
                operation=operation
            )
