# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请构造器 - 支持C/D依赖自动解决 (B级)
# @Time   : 2026-04-01
# @Author : 毛鹏
import uuid
from typing import Optional, List, Dict, Any

from core.base import BaseBuilder, BuilderContext
from core.enums import DependencyLevel
from ..budget.budget_builder import BudgetBuilder
from ..user.user_builder import UserBuilder
from ...entities.reimbursement import ReimbursementEntity
from ...registry import register_builder
from ....api_manager import bdd_api_mock


@register_builder("reimbursement")
class ReimbursementBuilder(BaseBuilder[ReimbursementEntity]):
    """
    报销申请构造器 - B级模块（流程层）
    
    特性：
    1. 集成Strategy层（支持API/Mock/DB/Hybrid）
    2. 支持BuilderContext（追踪、清理、策略）
    3. 支持级联清理
    4. 【新增】智能依赖解决
    5. 【新增】快捷方法（create_submitted, create_approved）
    
    使用示例：
        # 基础用法
        builder = ReimbursementBuilder(token="xxx")
        reimb = builder.create(user_id=1, amount=1000)
        
        # 【新增】快捷方法 - 创建并提交
        reimb = builder.create_submitted(user_id=1, amount=1000)
        
        # 【新增】快捷方法 - 创建并审批通过
        reimb = builder.create_approved(user_id=1, amount=1000)
        
        # 使用Mock策略（单元测试）
        from auto_tests.bdd_api_mock.data_factory.strategies import MockStrategy
        context = BuilderContext(strategy=MockStrategy())
        builder = ReimbursementBuilder(context=context)
        reimb = builder.create(user_id=1, amount=1000)  # 不调用真实API
        
        # 级联清理
        with ReimbursementBuilder(token="xxx", context=BuilderContext(cascade_cleanup=True)) as builder:
            reimb = builder.create(user_id=1, amount=1000)
        # 自动清理
    """

    # 依赖层级：B级（依赖C/D）
    DEPENDENCY_LEVEL = DependencyLevel.LEVEL_B

    # 依赖预算与用户Builder（Budget会继续依赖Org）
    DEPENDENCIES = [BudgetBuilder, UserBuilder]

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
        self._created = []

    def _prepare_dependencies(self, **kwargs) -> Dict[str, Any]:
        """
        【智能依赖解决】准备依赖数据

        B级模块依赖：User + Budget(→Org)

        @param kwargs: 原始参数
        @return: 补充后的参数
        """
        if "amount" not in kwargs:
            kwargs["amount"] = 100.00

        if "reason" not in kwargs:
            kwargs["reason"] = f"差旅报销 - {uuid.uuid4().hex[:6]}"

        if self.context.auto_prepare_deps:
            if "user_id" not in kwargs:
                user_builder = self._get_or_create_builder(UserBuilder)
                user = user_builder.create(role="employee")
                kwargs["user_id"] = user.id if user and user.id else 1

            # 触发C→D依赖链，确保预算/组织准备完成
            budget_builder = self._get_or_create_builder(BudgetBuilder)
            budget_builder.create(total_amount=max(float(kwargs["amount"]) * 10, 500000))
        elif "user_id" not in kwargs:
            kwargs["user_id"] = 1

        return kwargs

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
        # 【智能依赖解决】自动准备依赖
        if auto_prepare_deps:
            kwargs = self._prepare_dependencies(**kwargs)

        # 构造实体（如果未传入）
        if entity is None:
            entity = self.build(**kwargs)

        # 使用Strategy创建
        created = self._do_create(entity)
        if created:
            self._created.append(created)
        return created

    def create_submitted(
            self,
            user_id: int = 1,
            amount: float = 100.00,
            reason: str = None,
            auto_prepare_deps: bool = True
    ) -> Optional[ReimbursementEntity]:
        """
        【快捷方法】创建并提交报销申请
        
        流程：创建 → 提交
        
        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param auto_prepare_deps: 是否自动准备依赖
        @return: 已提交的报销申请实体
        """
        # 创建报销申请
        reimb = self.create(
            user_id=user_id,
            amount=amount,
            reason=reason,
            auto_prepare_deps=auto_prepare_deps
        )

        if not reimb:
            return None

        # 提交报销申请
        success = self.submit(reimb.id)
        if success:
            # 刷新状态
            reimb = self.get_by_id(reimb.id)

        return reimb

    def create_approved(
            self,
            user_id: int = 1,
            amount: float = 100.00,
            reason: str = None,
            approver_id: int = None,
            auto_prepare_deps: bool = True
    ) -> Optional[ReimbursementEntity]:
        """
        【快捷方法】创建并审批通过的报销申请
        
        流程：创建 → 提交 → 审批通过
        
        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param approver_id: 审批人ID（默认使用系统管理员）
        @param auto_prepare_deps: 是否自动准备依赖
        @return: 已审批通过的报销申请实体
        """
        # 创建并提交
        reimb = self.create_submitted(
            user_id=user_id,
            amount=amount,
            reason=reason,
            auto_prepare_deps=auto_prepare_deps
        )

        if not reimb:
            return None

        # 审批通过
        success = self.approve(reimb.id, approver_id=approver_id)
        if success:
            # 刷新状态
            reimb = self.get_by_id(reimb.id)

        return reimb

    def create_rejected(
            self,
            user_id: int = 1,
            amount: float = 100.00,
            reason: str = None,
            reject_reason: str = "不符合报销标准",
            approver_id: int = None,
            auto_prepare_deps: bool = True
    ) -> Optional[ReimbursementEntity]:
        """
        【快捷方法】创建并被拒绝的报销申请
        
        流程：创建 → 提交 → 审批拒绝
        
        @param user_id: 用户ID
        @param amount: 报销金额
        @param reason: 报销原因
        @param reject_reason: 拒绝原因
        @param approver_id: 审批人ID
        @param auto_prepare_deps: 是否自动准备依赖
        @return: 已被拒绝的报销申请实体
        """
        # 创建并提交
        reimb = self.create_submitted(
            user_id=user_id,
            amount=amount,
            reason=reason,
            auto_prepare_deps=auto_prepare_deps
        )

        if not reimb:
            return None

        # 审批拒绝
        success = self.reject(reimb.id, reject_reason=reject_reason, approver_id=approver_id)
        if success:
            # 刷新状态
            reimb = self.get_by_id(reimb.id)

        return reimb

    def submit(self, reimbursement_id: int) -> bool:
        """
        提交报销申请
        
        @param reimbursement_id: 报销申请ID
        @return: 是否提交成功
        """
        result = bdd_api_mock.reimbursement.submit_reimbursement(reimbursement_id)
        return result.get("code") == 200

    def approve(self, reimbursement_id: int, approver_id: int = None) -> bool:
        """
        审批通过报销申请
        
        @param reimbursement_id: 报销申请ID
        @param approver_id: 审批人ID
        @return: 是否审批成功
        """
        result = bdd_api_mock.reimbursement.approve_reimbursement(
            reimbursement_id,
            approver_id=approver_id
        )
        return result.get("code") == 200

    def reject(self, reimbursement_id: int, reject_reason: str = "", approver_id: int = None) -> bool:
        """
        拒绝报销申请
        
        @param reimbursement_id: 报销申请ID
        @param reject_reason: 拒绝原因
        @param approver_id: 审批人ID
        @return: 是否拒绝成功
        """
        result = bdd_api_mock.reimbursement.reject_reimbursement(
            reimbursement_id,
            reject_reason=reject_reason,
            approver_id=approver_id
        )
        return result.get("code") == 200

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
        result = bdd_api_mock.reimbursement.get_reimbursements()

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

    def is_approved(self, reimbursement_id: int) -> bool:
        """
        【新增】检查报销申请是否已审批通过

        @param reimbursement_id: 报销申请ID
        @return: 是否已审批通过
        """
        status = self.get_status(reimbursement_id)
        return status == "approved"

    def is_rejected(self, reimbursement_id: int) -> bool:
        """
        【新增】检查报销申请是否已被拒绝

        @param reimbursement_id: 报销申请ID
        @return: 是否已被拒绝
        """
        status = self.get_status(reimbursement_id)
        return status == "rejected"

    def cleanup(self):
        """
        清理创建的数据
        """
        self._created.clear()
