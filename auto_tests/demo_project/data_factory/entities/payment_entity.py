# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 付款单实体
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
付款单实体模块

定义付款单数据结构，支持：
- 付款单生命周期管理
- 报销申请关联
- 支付状态追踪
- 智能工厂方法
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from core.base import BaseEntity


def uuid_short() -> str:
    """生成短UUID"""
    return str(uuid.uuid4())[:8]


@dataclass
class PaymentEntity(BaseEntity):
    """
    付款单实体
    
    Attributes:
        id: 付款单ID
        reimbursement_id: 关联报销申请ID
        amount: 付款金额
        payee: 收款人
        bank_account: 银行账号
        bank_name: 银行名称
        status: 状态（pending/paid/failed/cancelled）
        pay_date: 实际付款日期
        pay_method: 付款方式
        reference_no: 付款参考号
        metadata: 扩展元数据
    """

    # 基础字段
    id: Optional[str] = None
    reimbursement_id: Optional[str] = None

    # 付款信息
    amount: float = 0.0
    payee: str = ""
    bank_account: str = ""
    bank_name: str = ""

    # 状态字段
    status: str = "pending"  # pending, paid, failed, cancelled

    # 支付详情
    pay_date: Optional[date] = None
    pay_method: str = ""  # bank_transfer, alipay, wechat, cash
    reference_no: str = ""

    # 审批信息
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = f"payment_{uuid_short()}"
        if not self.reference_no:
            self.reference_no = f"PAY{datetime.now().strftime('%Y%m%d')}{self.id[-4:]}"

    # ==================== 业务行为 ====================

    def pay(self, pay_method: str = "bank_transfer", reference_no: str = "") -> bool:
        """
        执行付款
        
        Args:
            pay_method: 付款方式
            reference_no: 付款参考号
        
        Returns:
            bool: 是否成功
        """
        if self.status != "pending":
            return False

        self.status = "paid"
        self.pay_date = date.today()
        self.pay_method = pay_method
        if reference_no:
            self.reference_no = reference_no
        self.updated_at = datetime.now()
        return True

    def fail(self, reason: str = ""):
        """
        标记付款失败
        
        Args:
            reason: 失败原因
        """
        self.status = "failed"
        self.metadata["fail_reason"] = reason
        self.updated_at = datetime.now()

    def cancel(self, reason: str = ""):
        """
        取消付款
        
        Args:
            reason: 取消原因
        """
        if self.status == "paid":
            return False

        self.status = "cancelled"
        self.metadata["cancel_reason"] = reason
        self.updated_at = datetime.now()
        return True

    def approve(self, approver_id: str):
        """
        审批通过
        
        Args:
            approver_id: 审批人ID
        """
        self.approved_by = approver_id
        self.approved_at = datetime.now()
        self.updated_at = datetime.now()

    def is_pending(self) -> bool:
        """检查是否待付款"""
        return self.status == "pending"

    def is_paid(self) -> bool:
        """检查是否已付款"""
        return self.status == "paid"

    def is_failed(self) -> bool:
        """检查是否付款失败"""
        return self.status == "failed"

    def is_cancelled(self) -> bool:
        """检查是否已取消"""
        return self.status == "cancelled"

    def can_pay(self) -> bool:
        """检查是否可以付款"""
        return self.status == "pending" and self.approved_by is not None

    # ==================== 智能工厂方法 ====================

    @classmethod
    def for_reimbursement(cls, reimbursement_id: str, amount: float, **kwargs) -> "PaymentEntity":
        """
        为报销申请创建付款单
        
        Args:
            reimbursement_id: 报销申请ID
            amount: 付款金额
            **kwargs: 其他属性
        
        Returns:
            PaymentEntity: 付款单实体
        """
        return cls(
            reimbursement_id=reimbursement_id,
            amount=amount,
            **kwargs
        )

    @classmethod
    def with_bank_info(cls, payee: str, bank_account: str, bank_name: str, **kwargs) -> "PaymentEntity":
        """
        创建带银行信息的付款单
        
        Args:
            payee: 收款人
            bank_account: 银行账号
            bank_name: 银行名称
            **kwargs: 其他属性
        
        Returns:
            PaymentEntity: 付款单实体
        """
        return cls(
            payee=payee,
            bank_account=bank_account,
            bank_name=bank_name,
            pay_method="bank_transfer",
            **kwargs
        )

    @classmethod
    def with_alipay(cls, payee: str, alipay_account: str, **kwargs) -> "PaymentEntity":
        """
        创建支付宝付款单
        
        Args:
            payee: 收款人
            alipay_account: 支付宝账号
            **kwargs: 其他属性
        
        Returns:
            PaymentEntity: 付款单实体
        """
        return cls(
            payee=payee,
            bank_account=alipay_account,
            pay_method="alipay",
            **kwargs
        )

    @classmethod
    def paid_payment(cls, amount: float, pay_date: date = None, **kwargs) -> "PaymentEntity":
        """
        创建已付款的付款单
        
        Args:
            amount: 付款金额
            pay_date: 付款日期
            **kwargs: 其他属性
        
        Returns:
            PaymentEntity: 付款单实体
        """
        payment = cls(
            amount=amount,
            status="paid",
            pay_date=pay_date or date.today(),
            **kwargs
        )
        return payment

    @classmethod
    def random(cls) -> "PaymentEntity":
        """
        随机创建付款单
        
        Returns:
            PaymentEntity: 随机付款单实体
        """
        import random
        methods = ["bank_transfer", "alipay", "wechat", "cash"]
        return cls(
            amount=random.choice([100, 500, 1000, 5000, 10000]),
            pay_method=random.choice(methods),
            payee=f"收款人_{uuid_short()}",
        )

    # ==================== 验证方法 ====================

    def validate(self) -> bool:
        """验证付款单数据"""
        if self.amount <= 0:
            return False
        if not self.payee:
            return False
        if self.status not in ["pending", "paid", "failed", "cancelled"]:
            return False
        return True

    def get_dependencies(self) -> List[str]:
        """获取依赖的实体类型"""
        deps = []
        if self.reimbursement_id:
            deps.append("ReimbursementEntity")
        return deps

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "reimbursement_id": self.reimbursement_id,
            "amount": self.amount,
            "payee": self.payee,
            "bank_account": self.bank_account,
            "bank_name": self.bank_name,
            "status": self.status,
            "pay_date": self.pay_date.isoformat() if self.pay_date else None,
            "pay_method": self.pay_method,
            "reference_no": self.reference_no,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
