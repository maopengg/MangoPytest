# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请构造器 - 使用Entity的新版本 (D级)
# @Time   : 2026-04-01
# @Author : 毛鹏
from typing import Optional, List, Dict, Any
import uuid

from ..base_builder import BaseBuilder, BuilderContext, DependencyLevel
from ...entities.reimbursement import ReimbursementEntity
from ...registry import register_builder
from ....api_manager import demo_project


@register_builder("reimbursement")
class ReimbursementBuilder(BaseBuilder[ReimbursementEntity]):
    """
    报销申请构造器 - D级模块（基础层）
    
    特性：
    1. 集成Strategy层（支持API/Mock/DB/Hybrid）
    2. 支持BuilderContext（追踪、清理、策略）
    3. 支持级联清理
    
    使用示例：
        # 基础用法
        builder = ReimbursementBuilder(token="xxx")
        reimb = builder.create(user_id=1, amount=1000)
        
        # 使用Mock策略（单元测试）
        from auto_test.demo_project.data_factory.strategies import MockStrategy
        context = BuilderContext(strategy=MockStrategy())
        builder = ReimbursementBuilder(context=context)
        reimb = builder.create(user_id=1, amount=1000)  # 不调用真实API
        
        # 级联清理
        with ReimbursementBuilder(token="xxx", context=BuilderContext(cascade_cleanup=True)) as builder:
            reimb = builder.create(user_id=1, amount=1000)
        # 自动清理
    """
    
    # 依赖层级：D级（最底层，无依赖）
    DEPENDENCY_LEVEL = DependencyLevel.LEVEL_D
    
    # 无依赖（D级是基础层）
    DEPENDENCIES = []

    def __init__(
        self,
        token: str = None,
        context: BuilderContext = None,
        strategy=None,
        parent_builders=None,
        factory=None
    ):
        """
        初始化报销申请构造器
        
        @param token: 认证token
        @param context: Builder上下文（追踪、策略、清理配置）
        @param strategy: 数据策略（覆盖context中的策略）
        @param parent_builders: 父Builder字典（依赖注入）
        @param factory: 数据工厂实例
        """
        super().__init__(
            token=token,
            context=context,
            strategy=strategy,
            parent_builders=parent_builders,
            factory=factory
        )

    def build(
        self, user_id: int = 1, amount: float = 100.00, reason: str = None
    ) -> ReimbursementEntity:
        """
        构造报销申请实体（不调用API）

        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @return: 报销申请实体
        """
        return ReimbursementEntity(
            user_id=user_id,
            amount=amount,
            reason=reason or f"差旅报销 - {uuid.uuid4().hex[:6]}",
        )

    def create(
        self,
        entity: ReimbursementEntity = None,
        auto_prepare_deps: bool = True,
        **kwargs
    ) -> Optional[ReimbursementEntity]:
        """
        创建报销申请（调用Strategy）

        @param entity: 实体实例（不传则使用kwargs构造）
        @param auto_prepare_deps: 是否自动准备依赖数据（D级无依赖，此参数忽略）
        @param kwargs: 构造参数
        @return: 创建的报销申请实体
        """
        # 构造实体（如果未传入）
        if entity is None:
            entity = self.build(**kwargs)
        
        # 使用Strategy创建
        return self._do_create(entity)

    def update(
        self, entity: ReimbursementEntity, **kwargs
    ) -> Optional[ReimbursementEntity]:
        """
        更新报销申请（调用Strategy）
        
        @param entity: 实体实例
        @param kwargs: 更新字段
        @return: 更新后的实体
        """
        # 更新属性
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        # 使用Strategy更新
        result = self.context.strategy.update(entity, **kwargs)
        
        if result.success:
            self._register_created(result.entity)
            return result.entity
        return None

    def delete(self, entity_id: int) -> bool:
        """
        删除报销申请（调用Strategy）
        
        @param entity_id: 报销申请ID
        @return: 是否删除成功
        """
        result = self.context.strategy.delete(ReimbursementEntity, entity_id)
        return result.success

    def get_by_id(self, entity_id: int) -> Optional[ReimbursementEntity]:
        """
        根据ID获取报销申请（调用Strategy）
        
        @param entity_id: 报销申请ID
        @return: 报销申请实体
        """
        result = self.context.strategy.get_by_id(ReimbursementEntity, entity_id)
        
        if result.success:
            return result.entity
        return None

    def get_all(self) -> List[ReimbursementEntity]:
        """
        获取所有报销申请
        
        @return: 报销申请实体列表
        """
        # 使用API模块获取（兼容旧代码）
        result = demo_project.reimbursement.get_reimbursements()

        if result.get("code") == 200:
            data_list = result["data"]
            return [ReimbursementEntity.from_api_response(d) for d in data_list]

        return []

    def get_by_user(self, user_id: int) -> List[ReimbursementEntity]:
        """
        根据用户ID获取报销申请

        @param user_id: 用户ID
        @return: 报销申请实体列表
        """
        all_reimbursements = self.get_all()
        return [r for r in all_reimbursements if r.user_id == user_id]

    def get_status(self, reimbursement_id: int) -> Optional[str]:
        """
        获取报销申请状态

        @param reimbursement_id: 报销申请ID
        @return: 状态字符串
        """
        entity = self.get_by_id(reimbursement_id)
        if entity:
            return entity.status
        return None

    def is_pending(self, reimbursement_id: int) -> bool:
        """
        检查报销申请是否处于待审批状态

        @param reimbursement_id: 报销申请ID
        @return: 是否待审批
        """
        status = self.get_status(reimbursement_id)
        return status == "pending"
