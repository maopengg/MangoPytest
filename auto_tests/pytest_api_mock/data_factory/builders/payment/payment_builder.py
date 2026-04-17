# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 付款单构造器 - 支持D→C→B→A级联依赖解决 (A级)
# @Time   : 2026-04-01
# @Author : 毛鹏
import uuid
from typing import Optional, List, Dict, Any

from core.base import BaseBuilder, BuilderContext
from core.enums import DependencyLevel
from ..reimbursement.reimbursement_builder import ReimbursementBuilder
from ...entities.payment_entity import PaymentEntity
from ...registry import register_builder


@register_builder("payment")
class PaymentBuilder(BaseBuilder[PaymentEntity]):
    """
    付款单构造器 - A级模块（应用层）
    
    【核心特性】
    1. 自动解决依赖：Payment → Reimbursement → Budget → Org/User
    2. 级联构造：D→C→B→A 完整依赖链
    3. 智能依赖解决：自动创建缺失的依赖数据
    4. 快捷方法：create_paid, create_pending 等
    
    【使用示例】
        # 基础用法 - 自动解决所有依赖
        builder = PaymentBuilder(token="xxx")
        payment = builder.create(amount=5000)  # 自动创建报销单→预算→组织→用户
        
        # 使用已有报销单
        payment = builder.create(reimbursement_id=123, amount=5000)
        
        # 快捷方法 - 创建并付款
        payment = builder.create_paid(amount=5000)
        
        # 级联清理
        with PaymentBuilder(token="xxx", context=BuilderContext(cascade_cleanup=True)) as builder:
            payment = builder.create(amount=5000)
        # 自动清理：Payment → Reimbursement → Budget → Org
    """

    # 依赖层级：A级（最高层，依赖B级）
    DEPENDENCY_LEVEL = DependencyLevel.LEVEL_A

    # 【依赖声明】依赖的Builder类型
    # Payment(A级) → Reimbursement(B级)
    DEPENDENCIES = [ReimbursementBuilder]

    def __init__(
            self,
            token: str = None,
            context: BuilderContext = None,
            strategy=None,
            parent_builders=None,
            factory=None
    ):
        """
        初始化付款单构造器
        
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

        # 延迟导入依赖Builder以避免循环导入
        self._reimb_builder = None

    def _get_reimbursement_builder(self):
        """获取或创建报销单Builder"""
        if self._reimb_builder is None:
            self._reimb_builder = self._get_or_create_builder(ReimbursementBuilder)
        return self._reimb_builder

    def _prepare_dependencies(self, **kwargs) -> Dict[str, Any]:
        """
        【智能依赖解决】准备依赖数据
        
        自动解决依赖链：Payment → Reimbursement → Budget → Org/User
        
        @param kwargs: 原始参数
        @return: 补充依赖后的参数
        """
        # 如果已提供 reimbursement_id，无需解决依赖
        if "reimbursement_id" in kwargs and kwargs["reimbursement_id"]:
            return kwargs

        # 【智能依赖解决】自动创建已审批的报销单
        if self.context.auto_prepare_deps:
            reimb_builder = self._get_reimbursement_builder()
            if reimb_builder:
                # 获取金额
                amount = kwargs.get("amount", 1000.00)

                # 自动创建已审批的报销单（触发B→C→D构造）
                reimb = reimb_builder.create_approved(
                    amount=amount,
                    auto_prepare_deps=True  # 级联自动解决
                )

                if reimb:
                    kwargs["reimbursement_id"] = reimb.id
                    # 如果未指定金额，使用报销单金额
                    if "amount" not in kwargs:
                        kwargs["amount"] = reimb.amount

        # 补充其他默认值
        if "payee" not in kwargs:
            kwargs["payee"] = "供应商"

        if "pay_method" not in kwargs:
            kwargs["pay_method"] = "bank_transfer"

        return kwargs

    def build(
            self,
            reimbursement_id: int = None,
            amount: float = 0.0,
            payee: str = None,
            pay_method: str = "bank_transfer",
            **kwargs
    ) -> PaymentEntity:
        """
        构造付款单实体（不调用API）

        @param reimbursement_id: 关联报销单ID
        @param amount: 付款金额
        @param payee: 收款人
        @param pay_method: 付款方式
        @return: 付款单实体
        """
        return PaymentEntity(
            reimbursement_id=reimbursement_id,
            amount=amount,
            payee=payee or f"供应商_{uuid.uuid4().hex[:6]}",
            pay_method=pay_method,
            status="pending",
            **kwargs
        )

    def create(
            self,
            entity: PaymentEntity = None,
            auto_prepare_deps: bool = True,
            **kwargs
    ) -> Optional[PaymentEntity]:
        """
        创建付款单（调用Strategy）
        
        【智能依赖解决】如果未提供 reimbursement_id，自动创建已审批的报销单

        @param entity: 实体实例（不传则使用kwargs构造）
        @param auto_prepare_deps: 是否自动准备依赖数据（自动创建报销单）
        @param kwargs: 构造参数
        @return: 创建的付款单实体
        """
        # 【智能依赖解决】自动准备依赖
        if auto_prepare_deps:
            kwargs = self._prepare_dependencies(**kwargs)

        # 构造实体（如果未传入）
        if entity is None:
            entity = self.build(**kwargs)

        # 使用Strategy创建
        return self._do_create(entity)

    def create_paid(
            self,
            reimbursement_id: int = None,
            amount: float = 0.0,
            payee: str = None,
            pay_method: str = "bank_transfer",
            auto_prepare_deps: bool = True
    ) -> Optional[PaymentEntity]:
        """
        【快捷方法】创建并已付款的付款单
        
        流程：创建 → 付款
        
        @param reimbursement_id: 关联报销单ID（不提供则自动创建）
        @param amount: 付款金额
        @param payee: 收款人
        @param pay_method: 付款方式
        @param auto_prepare_deps: 是否自动准备依赖
        @return: 已付款的付款单实体
        """
        # 创建付款单
        payment = self.create(
            reimbursement_id=reimbursement_id,
            amount=amount,
            payee=payee,
            pay_method=pay_method,
            auto_prepare_deps=auto_prepare_deps
        )

        if not payment:
            return None

        # 执行付款
        success = self.pay(payment.id, pay_method=pay_method)
        if success:
            # 刷新状态
            payment = self.get_by_id(payment.id)

        return payment

    def create_failed(
            self,
            reimbursement_id: int = None,
            amount: float = 0.0,
            fail_reason: str = "余额不足",
            auto_prepare_deps: bool = True
    ) -> Optional[PaymentEntity]:
        """
        【快捷方法】创建并付款失败的付款单
        
        流程：创建 → 尝试付款 → 失败
        
        @param reimbursement_id: 关联报销单ID
        @param amount: 付款金额
        @param fail_reason: 失败原因
        @param auto_prepare_deps: 是否自动准备依赖
        @return: 付款失败的付款单实体
        """
        # 创建付款单
        payment = self.create(
            reimbursement_id=reimbursement_id,
            amount=amount,
            auto_prepare_deps=auto_prepare_deps
        )

        if not payment:
            return None

        # 标记失败
        success = self.fail(payment.id, reason=fail_reason)
        if success:
            # 刷新状态
            payment = self.get_by_id(payment.id)

        return payment

    def pay(self, payment_id: int, pay_method: str = "bank_transfer") -> bool:
        """
        执行付款
        
        @param payment_id: 付款单ID
        @param pay_method: 付款方式
        @return: 是否付款成功
        """
        # 使用API模块执行付款
        try:
            from ....api_manager import pytest_api_mock
            result = pytest_api_mock.payment.pay_payment(payment_id, pay_method=pay_method)
            return result.get("code") == 200
        except:
            # 模拟付款成功
            payment = self.get_by_id(payment_id)
            if payment:
                payment.pay(pay_method)
                return True
            return False

    def fail(self, payment_id: int, reason: str = "") -> bool:
        """
        标记付款失败
        
        @param payment_id: 付款单ID
        @param reason: 失败原因
        @return: 是否标记成功
        """
        payment = self.get_by_id(payment_id)
        if payment:
            payment.fail(reason)
            return True
        return False

    def cancel(self, payment_id: int, reason: str = "") -> bool:
        """
        取消付款
        
        @param payment_id: 付款单ID
        @param reason: 取消原因
        @return: 是否取消成功
        """
        payment = self.get_by_id(payment_id)
        if payment:
            return payment.cancel(reason)
        return False

    def update(self, entity: PaymentEntity, **kwargs) -> Optional[PaymentEntity]:
        """
        更新付款单
        
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

    def delete(self, entity_id: int, cascade: bool = None) -> bool:
        """
        删除付款单（支持级联清理）
        
        @param entity_id: 付款单ID
        @param cascade: 是否级联清理（默认使用context配置）
        @return: 是否删除成功
        """
        # 先获取付款单信息
        payment = self.get_by_id(entity_id)
        if not payment:
            return False

        # 使用Strategy删除
        result = self.context.strategy.delete(PaymentEntity, entity_id)

        # 级联清理上游依赖
        should_cascade = cascade if cascade is not None else self.context.cascade_cleanup
        if should_cascade and payment.reimbursement_id:
            reimb_builder = self._get_reimbursement_builder()
            if reimb_builder:
                try:
                    reimb_builder.delete(payment.reimbursement_id)
                except Exception as e:
                    print(f"级联清理报销单失败: {e}")

        return result.success

    def get_by_id(self, entity_id: int) -> Optional[PaymentEntity]:
        """
        根据ID获取付款单
        
        @param entity_id: 付款单ID
        @return: 付款单实体
        """
        result = self.context.strategy.get_by_id(PaymentEntity, entity_id)

        if result.success:
            return result.entity
        return None

    def get_all(self) -> List[PaymentEntity]:
        """
        获取所有付款单
        
        @return: 付款单实体列表
        """
        # 使用API模块获取
        try:
            from ....api_manager import pytest_api_mock
            result = pytest_api_mock.payment.get_payments()

            if result.get("code") == 200:
                data_list = result["data"]
                return [PaymentEntity(**d) for d in data_list]
        except:
            pass

        return []

    def get_by_reimbursement(self, reimbursement_id: int) -> List[PaymentEntity]:
        """
        根据报销单ID获取付款单
        
        @param reimbursement_id: 报销单ID
        @return: 付款单实体列表
        """
        all_payments = self.get_all()
        return [p for p in all_payments if p.reimbursement_id == reimbursement_id]

    def get_status(self, payment_id: int) -> Optional[str]:
        """
        获取付款单状态
        
        @param payment_id: 付款单ID
        @return: 状态字符串
        """
        entity = self.get_by_id(payment_id)
        if entity:
            return entity.status
        return None

    def is_pending(self, payment_id: int) -> bool:
        """
        检查是否待付款
        
        @param payment_id: 付款单ID
        @return: 是否待付款
        """
        status = self.get_status(payment_id)
        return status == "pending"

    def is_paid(self, payment_id: int) -> bool:
        """
        检查是否已付款
        
        @param payment_id: 付款单ID
        @return: 是否已付款
        """
        status = self.get_status(payment_id)
        return status == "paid"

    def is_failed(self, payment_id: int) -> bool:
        """
        检查是否付款失败
        
        @param payment_id: 付款单ID
        @return: 是否付款失败
        """
        status = self.get_status(payment_id)
        return status == "failed"


# 创建 __init__.py 使目录成为包
if __name__ == "__main__":
    # 测试代码
    print("PaymentBuilder 模块加载成功")
