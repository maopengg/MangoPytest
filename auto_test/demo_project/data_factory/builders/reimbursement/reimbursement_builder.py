# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请构造器 - 使用Entity的新版本 (D级)
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Optional, List
import uuid

from ..base_builder import BaseBuilder
from ...entities.reimbursement import ReimbursementEntity
from ...registry import register_builder
from ....api_manager import demo_project


@register_builder("reimbursement")
class ReimbursementBuilder(BaseBuilder[ReimbursementEntity]):
    """
    报销申请构造器 - D级模块（基础层）

    使用Entity进行数据构造和API调用
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)

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
        self, entity: ReimbursementEntity = None, **kwargs
    ) -> Optional[ReimbursementEntity]:
        """
        创建报销申请（调用API）

        @param entity: 实体实例（不传则使用kwargs构造）
        @param kwargs: 构造参数
        @return: 创建后的实体
        """
        if entity is None:
            entity = self.build(**kwargs)

        if not entity.validate():
            return None

        result = demo_project.reimbursement.create_reimbursement(
            user_id=entity.user_id, amount=entity.amount, reason=entity.reason
        )

        if result.get("code") == 200:
            data = result["data"]
            created_entity = ReimbursementEntity.from_api_response(data)
            self._register_created(created_entity)
            return created_entity

        return None

    def get_by_id(self, reimbursement_id: int) -> Optional[ReimbursementEntity]:
        """
        根据ID获取报销申请

        @param reimbursement_id: 报销申请ID
        @return: 报销申请实体
        """
        result = demo_project.reimbursement.get_reimbursement_by_id(reimbursement_id)

        if result.get("code") == 200:
            data = result["data"]
            return ReimbursementEntity.from_api_response(data)

        return None

    def update(self, entity: ReimbursementEntity) -> Optional[ReimbursementEntity]:
        """
        更新报销申请

        @param entity: 实体实例
        @return: 更新后的实体
        """
        result = demo_project.reimbursement.update_reimbursement(
            reimbursement_id=entity.id, **entity.to_api_payload()
        )

        if result.get("code") == 200:
            data = result["data"]
            return ReimbursementEntity.from_api_response(data)

        return None

    def delete(self, entity: ReimbursementEntity) -> bool:
        """
        删除报销申请

        @param entity: 实体实例
        @return: 是否删除成功
        """
        result = demo_project.reimbursement.delete_reimbursement(entity.id)

        if result.get("code") == 200:
            entity.mark_as_deleted()
            return True

        return False

    def get_all(self) -> List[ReimbursementEntity]:
        """
        获取所有报销申请

        @return: 报销申请实体列表
        """
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
