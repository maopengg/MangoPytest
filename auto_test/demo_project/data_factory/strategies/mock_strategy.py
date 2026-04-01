# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Mock策略 - 本地内存对象，用于单元测试
# @Time   : 2026-04-01
# @Author : 毛鹏
from typing import Type, Optional, Dict, Any, TypeVar, List
import uuid
from datetime import datetime

from .base_strategy import BaseStrategy, StrategyResult
from ..entities.base_entity import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class MockStrategy(BaseStrategy[T]):
    """
    Mock策略 - 本地内存对象操作
    
    所有数据存储在内存中，不调用真实API，执行速度最快。
    适用于：单元测试、快速原型验证、CI流水线加速
    
    特点：
    - 极速执行（无网络IO）
    - 完全隔离（不影响真实数据）
    - 易于控制（可手动设置各种状态）
    - 不支持真实业务规则验证
    
    使用示例：
        strategy = MockStrategy()
        
        # 创建用户
        result = strategy.create(UserEntity, username="test", password="123456")
        user = result.entity
        
        # 后续操作使用内存中的ID
        result = strategy.get_by_id(UserEntity, user.id)
    """
    
    # 内存存储：{实体类名: {实体ID: 实体实例}}
    _storage: Dict[str, Dict[Any, BaseEntity]] = {}
    _id_counters: Dict[str, int] = {}
    
    def __init__(self, context: Optional[Any] = None, config: Optional[Dict] = None, seed_data: Optional[Dict] = None):
        """
        初始化Mock策略
        
        @param context: 执行上下文
        @param config: 配置
        @param seed_data: 初始种子数据 {实体类名: [实体数据字典]}
        """
        super().__init__(context, config)
        self.auto_generate_id = config.get("auto_generate_id", True) if config else True
        
        # 初始化种子数据
        if seed_data:
            self._init_seed_data(seed_data)
    
    def _init_seed_data(self, seed_data: Dict[str, List[Dict]]):
        """初始化种子数据"""
        for entity_name, data_list in seed_data.items():
            for data in data_list:
                # 动态获取实体类
                entity_class = self._get_entity_class(entity_name)
                if entity_class:
                    entity = entity_class(**data)
                    self._store_entity(entity)
    
    def _get_entity_class(self, entity_name: str) -> Optional[Type[BaseEntity]]:
        """根据名称获取实体类"""
        # 简单的映射，实际项目中可以使用更复杂的动态导入
        from ..entities import (
            UserEntity, ReimbursementEntity, DeptApprovalEntity,
            FinanceApprovalEntity, CEOApprovalEntity
        )
        mapping = {
            "UserEntity": UserEntity,
            "ReimbursementEntity": ReimbursementEntity,
            "DeptApprovalEntity": DeptApprovalEntity,
            "FinanceApprovalEntity": FinanceApprovalEntity,
            "CEOApprovalEntity": CEOApprovalEntity,
        }
        return mapping.get(entity_name)
    
    def _generate_id(self, entity_type: Type[T]) -> Any:
        """生成唯一ID"""
        entity_name = entity_type.__name__
        
        if entity_name not in self._id_counters:
            self._id_counters[entity_name] = 0
        
        self._id_counters[entity_name] += 1
        return self._id_counters[entity_name]
    
    def _get_storage(self, entity_type: Type[T]) -> Dict[Any, BaseEntity]:
        """获取实体内存存储"""
        entity_name = entity_type.__name__
        if entity_name not in self._storage:
            self._storage[entity_name] = {}
        return self._storage[entity_name]
    
    def _store_entity(self, entity: BaseEntity):
        """存储实体到内存"""
        storage = self._get_storage(entity.__class__)
        entity_id = getattr(entity, "id", None)
        if entity_id:
            storage[entity_id] = entity
    
    def create(self, entity_type: Type[T], **kwargs) -> StrategyResult:
        """
        在内存中创建实体
        
        @param entity_type: 实体类型
        @param kwargs: 实体属性
        @return: 策略执行结果
        """
        try:
            # 构造实体
            entity = entity_type(**kwargs)
            
            # 验证数据
            if hasattr(entity, "validate") and not entity.validate():
                return StrategyResult(
                    success=False,
                    error_code="VALIDATION_ERROR",
                    error_message="实体数据验证失败"
                )
            
            # 自动生成ID
            if self.auto_generate_id and not getattr(entity, "id", None):
                entity.id = self._generate_id(entity_type)
            
            # 设置时间戳
            now = datetime.now().isoformat()
            if hasattr(entity, "created_at") and not getattr(entity, "created_at", None):
                entity.created_at = now
            if hasattr(entity, "updated_at"):
                entity.updated_at = now
            
            # 存储到内存
            self._store_entity(entity)
            
            # 追踪
            self._track_entity(entity, "created")
            
            return StrategyResult(
                success=True,
                entity=entity,
                raw_data=entity.__dict__ if hasattr(entity, "__dict__") else {}
            )
            
        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )
    
    def update(self, entity: T, **kwargs) -> StrategyResult:
        """
        在内存中更新实体
        
        @param entity: 实体实例
        @param kwargs: 更新属性
        @return: 策略执行结果
        """
        try:
            entity_id = getattr(entity, "id", None)
            if not entity_id:
                return StrategyResult(
                    success=False,
                    error_code="NO_ENTITY_ID",
                    error_message="实体没有ID，无法更新"
                )
            
            storage = self._get_storage(entity.__class__)
            
            if entity_id not in storage:
                return StrategyResult(
                    success=False,
                    error_code="NOT_FOUND",
                    error_message=f"实体 {entity.__class__.__name__} ID={entity_id} 不存在"
                )
            
            # 更新属性
            stored_entity = storage[entity_id]
            for key, value in kwargs.items():
                if hasattr(stored_entity, key):
                    setattr(stored_entity, key, value)
            
            # 更新时间戳
            if hasattr(stored_entity, "updated_at"):
                stored_entity.updated_at = datetime.now().isoformat()
            
            # 追踪
            self._track_entity(stored_entity, "updated")
            
            return StrategyResult(
                success=True,
                entity=stored_entity,
                raw_data=stored_entity.__dict__ if hasattr(stored_entity, "__dict__") else {}
            )
            
        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )
    
    def delete(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        从内存中删除实体
        
        @param entity_type: 实体类型
        @param entity_id: 实体ID
        @return: 策略执行结果
        """
        try:
            storage = self._get_storage(entity_type)
            
            if entity_id not in storage:
                return StrategyResult(
                    success=False,
                    error_code="NOT_FOUND",
                    error_message=f"实体 {entity_type.__name__} ID={entity_id} 不存在"
                )
            
            # 获取实体用于追踪
            entity = storage[entity_id]
            
            # 删除
            del storage[entity_id]
            
            # 追踪
            self._track_entity(entity, "deleted")
            
            return StrategyResult(
                success=True,
                raw_data={"deleted_id": entity_id}
            )
            
        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )
    
    def get_by_id(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        从内存中根据ID获取实体
        
        @param entity_type: 实体类型
        @param entity_id: 实体ID
        @return: 策略执行结果
        """
        try:
            storage = self._get_storage(entity_type)
            
            if entity_id not in storage:
                return StrategyResult(
                    success=False,
                    error_code="NOT_FOUND",
                    error_message=f"实体 {entity_type.__name__} ID={entity_id} 不存在"
                )
            
            entity = storage[entity_id]
            
            return StrategyResult(
                success=True,
                entity=entity,
                raw_data=entity.__dict__ if hasattr(entity, "__dict__") else {}
            )
            
        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )
    
    def get_all(self, entity_type: Type[T]) -> List[T]:
        """获取内存中所有实体（Mock特有方法）"""
        storage = self._get_storage(entity_type)
        return list(storage.values())
    
    def clear(self, entity_type: Optional[Type[T]] = None):
        """
        清空内存数据
        
        @param entity_type: 指定实体类型（None则清空所有）
        """
        if entity_type:
            entity_name = entity_type.__name__
            if entity_name in self._storage:
                self._storage[entity_name].clear()
        else:
            self._storage.clear()
            self._id_counters.clear()
    
    def count(self, entity_type: Type[T]) -> int:
        """获取内存中实体数量"""
        storage = self._get_storage(entity_type)
        return len(storage)
