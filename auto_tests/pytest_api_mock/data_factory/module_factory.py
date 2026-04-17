# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 模块数据工厂
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any

from .base_builder import ApprovalFlowBuilder, UserDataBuilder
from .factory_manager import data_factory_manager


class ModuleDataFactory:
    """模块数据工厂 - 负责具体模块的数据创建和清理"""

    def __init__(self):
        self.flow_builder = ApprovalFlowBuilder()
        self.user_builder = UserDataBuilder()

        # 注册模块依赖关系
        self._register_dependencies()

    def _register_dependencies(self):
        """注册模块依赖关系"""
        # D模块：基础数据（无依赖）
        data_factory_manager.register_dependency(
            module_name="module_d",
            dependencies=[],
            factory_method="create_module_d_data",
            cleanup_method="cleanup_module_d_data"
        )

        # C模块：依赖D模块
        data_factory_manager.register_dependency(
            module_name="module_c",
            dependencies=["module_d"],
            factory_method="create_module_c_data",
            cleanup_method="cleanup_module_c_data"
        )

        # B模块：依赖C模块
        data_factory_manager.register_dependency(
            module_name="module_b",
            dependencies=["module_c"],
            factory_method="create_module_b_data",
            cleanup_method="cleanup_module_b_data"
        )

        # A模块：依赖B模块
        data_factory_manager.register_dependency(
            module_name="module_a",
            dependencies=["module_b"],
            factory_method="create_module_a_data",
            cleanup_method="cleanup_module_a_data"
        )

    # D模块数据创建和清理
    def create_module_d_data(self, **kwargs) -> Dict[str, Any]:
        """创建D模块数据（基础数据）"""
        print("创建D模块数据...")

        # 使用API管理模块创建基础数据
        from auto_tests.pytest_api_mock.api_manager.auth import AuthAPI
        from auto_tests.pytest_api_mock.api_manager.user import UserAPI

        auth_api = AuthAPI()
        user_api = UserAPI()

        # 创建基础用户数据
        base_user = self.user_builder.build_custom_data(
            username="admin_user",
            role="admin",
            department="系统管理部"
        )

        return {
            "base_user": base_user,
            "system_config": {
                "config_id": "sys_config_001",
                "config_name": "系统基础配置",
                "config_value": "default"
            },
            "apis": {
                "auth": auth_api,
                "user": user_api
            }
        }

    def cleanup_module_d_data(self, data: Dict[str, Any]):
        """清理D模块数据"""
        print("清理D模块数据...")

    # C模块数据创建和清理  
    def create_module_c_data(self, **kwargs) -> Dict[str, Any]:
        """创建C模块数据（依赖D模块）"""
        print("创建C模块数据...")

        # 获取D模块已创建的数据
        module_d_data = data_factory_manager.get_created_data("module_d")
        if not module_d_data:
            raise ValueError("D模块数据未创建，无法创建C模块数据")

        # 使用API管理模块
        from auto_tests.pytest_api_mock.api_manager.product import ProductAPI

        product_api = ProductAPI()

        # 基于D模块数据创建C模块数据
        flow_template = self.flow_builder.build_custom_data(
            flow_name="标准审批流程模板",
            flow_code="TEMPLATE_STANDARD",
            description="标准审批流程模板"
        )

        return {
            "flow_template": flow_template,
            "dependent_data": module_d_data,
            "apis": {
                "product": product_api
            }
        }

    def cleanup_module_c_data(self, data: Dict[str, Any]):
        """清理C模块数据"""
        print("清理C模块数据...")

    # B模块数据创建和清理
    def create_module_b_data(self, **kwargs) -> Dict[str, Any]:
        """创建B模块数据（依赖C模块）"""
        print("创建B模块数据...")

        # 获取C模块已创建的数据
        module_c_data = data_factory_manager.get_created_data("module_c")
        if not module_c_data:
            raise ValueError("C模块数据未创建，无法创建B模块数据")

        # 使用API管理模块
        from auto_tests.pytest_api_mock.api_manager.order import OrderAPI

        order_api = OrderAPI()

        # 基于C模块数据创建B模块数据
        flow_instance = self.flow_builder.build_custom_data(
            flow_name="采购审批流程",
            flow_code="FLOW_PURCHASE_001",
            description="采购订单审批流程"
        )

        # 创建审批节点
        approval_nodes = [
            {
                "node_id": "node_001",
                "node_name": "部门经理审批",
                "approver": "dept_manager_001",
                "order": 1
            },
            {
                "node_id": "node_002",
                "node_name": "财务审批",
                "approver": "finance_001",
                "order": 2
            }
        ]

        return {
            "flow_instance": flow_instance,
            "approval_nodes": approval_nodes,
            "dependent_data": module_c_data,
            "apis": {
                "order": order_api
            }
        }

    def cleanup_module_b_data(self, data: Dict[str, Any]):
        """清理B模块数据"""
        print("清理B模块数据...")

    # A模块数据创建和清理
    def create_module_a_data(self, **kwargs) -> Dict[str, Any]:
        """创建A模块数据（依赖B模块）"""
        print("创建A模块数据...")

        # 获取B模块已创建的数据
        module_b_data = data_factory_manager.get_created_data("module_b")
        if not module_b_data:
            raise ValueError("B模块数据未创建，无法创建A模块数据")

        # 使用API管理模块
        from auto_tests.pytest_api_mock.api_manager.data import DataAPI
        from auto_tests.pytest_api_mock.api_manager.system import SystemAPI
        from auto_tests.pytest_api_mock.api_manager.file import FileAPI

        data_api = DataAPI()
        system_api = SystemAPI()
        file_api = FileAPI()

        # 基于B模块数据创建A模块数据
        approval_application = {
            "application_id": f"APP_{self.user_builder.generate_random_string(8).upper()}",
            "applicant": "test_user_001",
            "apply_time": self.user_builder.generate_timestamp(),
            "flow_instance_id": module_b_data["flow_instance"]["flow_code"],
            "status": "pending",
            "apply_data": {
                "purchase_amount": 5000,
                "purchase_items": ["办公用品", "设备采购"],
                "reason": "日常办公需求"
            }
        }

        return {
            "approval_application": approval_application,
            "current_node": module_b_data["approval_nodes"][0],
            "dependent_data": module_b_data,
            "apis": {
                "data": data_api,
                "system": system_api,
                "file": file_api
            }
        }

    def cleanup_module_a_data(self, data: Dict[str, Any]):
        """清理A模块数据"""
        print("清理A模块数据...")

    def prepare_test_data(self, target_module: str, **kwargs) -> Dict[str, Any]:
        """为指定模块准备测试数据"""
        return data_factory_manager.create_data_for_module(target_module, self, **kwargs)

    def cleanup_test_data(self, target_module: str):
        """清理指定模块的测试数据"""
        data_factory_manager.cleanup_data_for_module(target_module, self)
