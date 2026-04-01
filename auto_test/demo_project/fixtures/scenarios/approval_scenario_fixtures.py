# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批流场景fixtures - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.data_factory.scenarios import (
    FullApprovalWorkflowScenario,
    RejectionWorkflowScenario,
    CreateReimbursementScenario,
)


@pytest.fixture
def create_reimbursement_scenario(authenticated_client) -> CreateReimbursementScenario:
    """
    创建报销申请场景Fixture

    使用示例:
        def test_create_reimbursement(create_reimbursement_scenario):
            result = create_reimbursement_scenario.execute(user_id=1, amount=100.00, reason="测试")
            assert result.success
            assert result.get_entity("reimbursement") is not None
    """
    scenario = CreateReimbursementScenario(token=authenticated_client.token)
    yield scenario
    scenario.cleanup()


@pytest.fixture
def full_approval_scenario(authenticated_client) -> FullApprovalWorkflowScenario:
    """
    完整4级审批流程场景Fixture

    使用示例:
        def test_full_approval(full_approval_scenario):
            result = full_approval_scenario.execute(user_id=1, amount=5000.00)
            assert result.success
            assert result.data.get("final_status") == "ceo_approved"
    """
    scenario = FullApprovalWorkflowScenario(token=authenticated_client.token)
    yield scenario
    scenario.cleanup()


@pytest.fixture
def rejection_scenario(authenticated_client) -> RejectionWorkflowScenario:
    """
    拒绝流程场景Fixture

    使用示例:
        def test_rejection(rejection_scenario):
            result = rejection_scenario.execute(reject_at="dept", user_id=1, amount=1000.00)
            assert result.success
    """
    scenario = RejectionWorkflowScenario(token=authenticated_client.token)
    yield scenario
    scenario.cleanup()


@pytest.fixture
def full_approval_workflow(full_approval_scenario):
    """
    完整审批流程数据Fixture
    直接返回执行结果

    使用示例:
        def test_with_workflow(full_approval_workflow):
            assert full_approval_workflow.success
            reimbursement = full_approval_workflow.get_entity("reimbursement")
            assert reimbursement is not None
    """
    return full_approval_scenario.execute(
        user_id=1, amount=5000.00, reason="完整审批流程测试"
    )


@pytest.fixture
def dept_rejected_workflow(rejection_scenario):
    """
    部门审批拒绝场景Fixture
    """
    return rejection_scenario.execute(reject_at="dept", user_id=1, amount=1000.00)


@pytest.fixture
def finance_rejected_workflow(rejection_scenario):
    """
    财务审批拒绝场景Fixture
    """
    return rejection_scenario.execute(reject_at="finance", user_id=1, amount=2000.00)


@pytest.fixture
def ceo_rejected_workflow(rejection_scenario):
    """
    总经理审批拒绝场景Fixture
    """
    return rejection_scenario.execute(reject_at="ceo", user_id=1, amount=3000.00)


class ApprovalScenarios:
    """
    审批场景容器类
    提供便捷的审批工作流创建方法
    """

    def __init__(self, full_approval_scenario, rejection_scenario):
        self._full_approval = full_approval_scenario
        self._rejection = rejection_scenario

    def _entity_to_dict(self, entity):
        """将实体转换为字典"""
        if entity is None:
            return None
        # 优先使用 __dict__ 获取所有属性
        if hasattr(entity, "__dict__"):
            result = entity.__dict__.copy()
            # 移除内部属性
            result.pop("_is_new", None)
            result.pop("_is_deleted", None)
            return result
        if hasattr(entity, "to_api_payload"):
            return entity.to_api_payload()
        return str(entity)

    def create_full_approval_workflow(
        self,
        user_id: int = 1,
        amount: float = 1000.00,
        reason: str = None,
        approved: bool = True,
    ) -> dict:
        """创建完整审批工作流"""
        import uuid

        reason = reason or f"完整审批测试 - {uuid.uuid4().hex[:6]}"
        result = self._full_approval.execute(
            user_id=user_id, amount=amount, reason=reason
        )
        if result.success:
            return {
                "status": "fully_approved",
                "reimbursement": self._entity_to_dict(
                    result.get_entity("reimbursement")
                ),
                "dept_approval": self._entity_to_dict(
                    result.get_entity("dept_approval")
                ),
                "finance_approval": self._entity_to_dict(
                    result.get_entity("finance_approval")
                ),
                "ceo_approval": self._entity_to_dict(result.get_entity("ceo_approval")),
            }
        return {"status": "failed", "error": result.errors}

    def create_pending_at_dept(
        self, user_id: int = 1, amount: float = 1000.00, reason: str = None
    ) -> dict:
        """创建待部门审批状态的工作流"""
        import uuid
        from auto_test.demo_project.data_factory.scenarios import (
            CreateReimbursementScenario,
        )
        from auto_test.demo_project.data_factory.entities.reimbursement import (
            ReimbursementEntity,
        )

        reason = reason or f"待部门审批测试 - {uuid.uuid4().hex[:6]}"

        # 只创建报销申请，不创建审批
        create_scenario = CreateReimbursementScenario(
            token=self._full_approval.token, factory=self._full_approval.factory
        )
        result = create_scenario.execute(user_id=user_id, amount=amount, reason=reason)

        if result.success:
            return {
                "status": "pending_at_dept",
                "reimbursement": self._entity_to_dict(
                    result.get_entity("reimbursement")
                ),
            }
        return {"status": "failed", "error": result.errors}

    def create_pending_at_finance(
        self, user_id: int = 1, amount: float = 1000.00, reason: str = None
    ) -> dict:
        """创建待财务审批状态的工作流"""
        import uuid
        from auto_test.demo_project.data_factory.scenarios import (
            CreateReimbursementScenario,
        )
        from auto_test.demo_project.data_factory.entities.reimbursement import (
            ReimbursementEntity,
        )
        from auto_test.demo_project.data_factory.entities.dept_approval import (
            DeptApprovalEntity,
        )
        from auto_test.demo_project.api_manager import demo_project

        reason = reason or f"待财务审批测试 - {uuid.uuid4().hex[:6]}"

        # 创建报销申请
        create_scenario = CreateReimbursementScenario(
            token=self._full_approval.token, factory=self._full_approval.factory
        )
        result = create_scenario.execute(user_id=user_id, amount=amount, reason=reason)

        if not result.success:
            return {"status": "failed", "error": result.errors}

        reimbursement = result.get_entity("reimbursement")

        # 设置token
        if self._full_approval.token:
            demo_project.dept_approval.set_token(self._full_approval.token)
            demo_project.reimbursement.set_token(self._full_approval.token)

        # 创建部门审批
        dept_response = demo_project.dept_approval.create_dept_approval(
            reimbursement_id=reimbursement.id,
            approver_id=3,
            status="approved",
            comment="部门审批通过",
        )

        if dept_response.get("code") != 200:
            return {
                "status": "failed",
                "error": f"部门审批创建失败: {dept_response.get('message')}",
            }

        dept_entity = DeptApprovalEntity.from_api_response(dept_response["data"])

        # 重新获取报销申请状态
        reimbursement_response = demo_project.reimbursement.get_reimbursement_by_id(
            reimbursement.id
        )
        if reimbursement_response.get("code") == 200:
            reimbursement = ReimbursementEntity.from_api_response(
                reimbursement_response["data"]
            )

        return {
            "status": "pending_at_finance",
            "reimbursement": self._entity_to_dict(reimbursement),
            "dept_approval": self._entity_to_dict(dept_entity),
        }

    def create_pending_at_ceo(
        self, user_id: int = 1, amount: float = 1000.00, reason: str = None
    ) -> dict:
        """创建待CEO审批状态的工作流"""
        import uuid
        from auto_test.demo_project.data_factory.scenarios import (
            CreateReimbursementScenario,
        )
        from auto_test.demo_project.data_factory.entities.reimbursement import (
            ReimbursementEntity,
        )
        from auto_test.demo_project.data_factory.entities.dept_approval import (
            DeptApprovalEntity,
        )
        from auto_test.demo_project.data_factory.entities.finance_approval import (
            FinanceApprovalEntity,
        )
        from auto_test.demo_project.api_manager import demo_project

        reason = reason or f"待CEO审批测试 - {uuid.uuid4().hex[:6]}"

        # 创建报销申请
        create_scenario = CreateReimbursementScenario(
            token=self._full_approval.token, factory=self._full_approval.factory
        )
        result = create_scenario.execute(user_id=user_id, amount=amount, reason=reason)

        if not result.success:
            return {"status": "failed", "error": result.errors}

        reimbursement = result.get_entity("reimbursement")

        # 设置token
        if self._full_approval.token:
            demo_project.dept_approval.set_token(self._full_approval.token)
            demo_project.finance_approval.set_token(self._full_approval.token)
            demo_project.reimbursement.set_token(self._full_approval.token)

        # 创建部门审批
        dept_response = demo_project.dept_approval.create_dept_approval(
            reimbursement_id=reimbursement.id,
            approver_id=3,
            status="approved",
            comment="部门审批通过",
        )

        if dept_response.get("code") != 200:
            return {
                "status": "failed",
                "error": f"部门审批创建失败: {dept_response.get('message')}",
            }

        dept_entity = DeptApprovalEntity.from_api_response(dept_response["data"])

        # 创建财务审批
        finance_response = demo_project.finance_approval.create_finance_approval(
            reimbursement_id=reimbursement.id,
            dept_approval_id=dept_entity.id,
            approver_id=4,
            status="approved",
            comment="财务审批通过",
        )

        if finance_response.get("code") != 200:
            return {
                "status": "failed",
                "error": f"财务审批创建失败: {finance_response.get('message')}",
            }

        finance_entity = FinanceApprovalEntity.from_api_response(
            finance_response["data"]
        )

        # 重新获取报销申请状态
        reimbursement_response = demo_project.reimbursement.get_reimbursement_by_id(
            reimbursement.id
        )
        if reimbursement_response.get("code") == 200:
            reimbursement = ReimbursementEntity.from_api_response(
                reimbursement_response["data"]
            )

        return {
            "status": "pending_at_ceo",
            "reimbursement": self._entity_to_dict(reimbursement),
            "dept_approval": self._entity_to_dict(dept_entity),
            "finance_approval": self._entity_to_dict(finance_entity),
        }

    def create_dept_rejected_workflow(
        self, user_id: int, amount: float, reason: str, comment: str = "拒绝"
    ) -> dict:
        """创建部门拒绝工作流"""
        result = self._rejection.execute(
            reject_at="dept", user_id=user_id, amount=amount, reason=reason
        )
        if result.success:
            return {
                "status": "dept_rejected",
                "reimbursement": self._entity_to_dict(
                    result.get_entity("reimbursement")
                ),
                "dept_approval": self._entity_to_dict(
                    result.get_entity("dept_approval")
                ),
            }
        return {"status": "failed", "error": result.errors}

    def create_finance_rejected_workflow(
        self, user_id: int, amount: float, reason: str, comment: str = "拒绝"
    ) -> dict:
        """创建财务拒绝工作流"""
        result = self._rejection.execute(
            reject_at="finance", user_id=user_id, amount=amount, reason=reason
        )
        if result.success:
            return {
                "status": "finance_rejected",
                "reimbursement": self._entity_to_dict(
                    result.get_entity("reimbursement")
                ),
                "dept_approval": self._entity_to_dict(
                    result.get_entity("dept_approval")
                ),
                "finance_approval": self._entity_to_dict(
                    result.get_entity("finance_approval")
                ),
            }
        return {"status": "failed", "error": result.errors}

    def create_ceo_rejected_workflow(
        self, user_id: int, amount: float, reason: str, comment: str = "拒绝"
    ) -> dict:
        """创建CEO拒绝工作流"""
        result = self._rejection.execute(
            reject_at="ceo", user_id=user_id, amount=amount, reason=reason
        )
        if result.success:
            return {
                "status": "ceo_rejected",
                "reimbursement": self._entity_to_dict(
                    result.get_entity("reimbursement")
                ),
                "dept_approval": self._entity_to_dict(
                    result.get_entity("dept_approval")
                ),
                "finance_approval": self._entity_to_dict(
                    result.get_entity("finance_approval")
                ),
                "ceo_approval": self._entity_to_dict(result.get_entity("ceo_approval")),
            }
        return {"status": "failed", "error": result.errors}


@pytest.fixture
def approval_scenarios(full_approval_scenario, rejection_scenario):
    """
    审批场景集合Fixture

    使用示例:
        def test_workflow(approval_scenarios):
            workflow = approval_scenarios.create_full_approval_workflow(
                user_id=1, amount=5000.00, reason="测试"
            )
            assert workflow["status"] == "fully_approved"
    """
    return ApprovalScenarios(full_approval_scenario, rejection_scenario)
