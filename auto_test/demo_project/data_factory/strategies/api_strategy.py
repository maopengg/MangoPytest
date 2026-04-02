# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API策略 - 通过REST/GraphQL接口操作数据
# @Time   : 2026-04-01
# @Author : 毛鹏
from typing import Type, Optional, Dict, Any, TypeVar

from .base_strategy import BaseStrategy, StrategyResult
from ..entities.base_entity import BaseEntity
from ...api_manager import demo_project

T = TypeVar("T", bound=BaseEntity)


class APIStrategy(BaseStrategy[T]):
    """
    API策略 - 通过REST/GraphQL接口创建/更新/删除数据

    这是最可靠的策略，所有操作通过API完成，确保业务规则验证完整。
    适用于：功能测试、集成测试、生产环境验证

    特点：
    - 完整业务规则验证
    - 触发所有钩子（hooks）
    - 支持工作流状态流转
    - 最慢但最可靠

    使用示例：
        strategy = APIStrategy(token="xxx")
        result = strategy.create(UserEntity, username="test", password="123456")
        if result.success:
            user = result.entity
    """

    # API 路径映射配置（可根据实际项目调整）
    API_MAPPING = {
        # 实体类名 -> (模块名, 路径前缀)
        "UserEntity": ("user", "/users"),
        "ReimbursementEntity": ("reimbursement", "/reimbursements"),
        "DeptApprovalEntity": ("dept_approval", "/dept-approvals"),
        "FinanceApprovalEntity": ("finance_approval", "/finance-approvals"),
        "CEOApprovalEntity": ("ceo_approval", "/ceo-approvals"),
        "ProductEntity": ("product", "/products"),
        "OrderEntity": ("order", "/orders"),
    }

    def __init__(
        self,
        token: Optional[str] = None,
        context: Optional[Any] = None,
        config: Optional[Dict] = None,
    ):
        """
        初始化API策略

        @param token: 认证token
        @param context: 执行上下文
        @param config: 配置（timeout, retry等）
        """
        super().__init__(context, config)
        self.token = token
        self.timeout = config.get("timeout", 30) if config else 30
        self.retry_count = config.get("retry", 3) if config else 3

        # 设置token到API模块
        if token:
            self._set_token_to_apis(token)

    def _set_token_to_apis(self, token: str):
        """设置token到所有API模块"""
        for module_name in dir(demo_project):
            module = getattr(demo_project, module_name)
            if hasattr(module, "set_token"):
                module.set_token(token)

    def _get_api_module(self, entity_type: Type[T]):
        """根据实体类型获取对应的API模块"""
        entity_name = entity_type.__name__
        mapping = self.API_MAPPING.get(entity_name)

        if not mapping:
            raise ValueError(f"未找到实体 {entity_name} 的API映射配置")

        module_name, _ = mapping
        return getattr(demo_project, module_name)

    def create(self, entity_type: Type[T], **kwargs) -> StrategyResult:
        """
        通过API创建实体

        @param entity_type: 实体类型
        @param kwargs: 实体属性
        @return: 策略执行结果
        """
        try:
            # 构造实体（验证数据）
            entity = entity_type(**kwargs)
            if not entity.validate():
                return StrategyResult(
                    success=False,
                    error_code="VALIDATION_ERROR",
                    error_message="实体数据验证失败",
                )

            # 获取API模块
            api_module = self._get_api_module(entity_type)

            # 调用API创建
            # 注意：这里假设API模块有对应的create方法
            # 实际项目中可能需要根据实体类型动态调用
            result = self._call_create_api(api_module, entity)

            if result.get("code") == 200:
                # 创建成功，更新实体ID
                data = result.get("data", {})
                created_entity = entity_type.from_api_response(data)

                # 追踪实体
                self._track_entity(created_entity, "created")

                return StrategyResult(
                    success=True, entity=created_entity, raw_data=data
                )
            else:
                return StrategyResult(
                    success=False,
                    error_code=str(result.get("code")),
                    error_message=result.get("message", "API调用失败"),
                )

        except Exception as e:
            return StrategyResult(
                success=False, error_code="EXCEPTION", error_message=str(e)
            )

    def _call_create_api(self, api_module, entity: BaseEntity) -> Dict:
        """调用创建API（根据实体类型路由到正确的方法）"""
        entity_name = entity.__class__.__name__
        payload = (
            entity.to_api_payload()
            if hasattr(entity, "to_api_payload")
            else entity.__dict__
        )

        # 根据实体类型调用对应的API方法
        method_mapping = {
            "UserEntity": "create_user",
            "ReimbursementEntity": "create_reimbursement",
            "DeptApprovalEntity": "create_dept_approval",
            "FinanceApprovalEntity": "create_finance_approval",
            "CEOApprovalEntity": "create_ceo_approval",
            "ProductEntity": "create_product",
            "OrderEntity": "create_order",
        }

        method_name = method_mapping.get(entity_name)
        if not method_name:
            raise ValueError(f"未找到实体 {entity_name} 的创建方法映射")

        create_method = getattr(api_module, method_name)
        return create_method(**payload)

    def update(self, entity: T, **kwargs) -> StrategyResult:
        """
        通过API更新实体

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
                    error_message="实体没有ID，无法更新",
                )

            # 获取API模块
            api_module = self._get_api_module(entity.__class__)

            # 调用API更新
            result = self._call_update_api(api_module, entity, kwargs)

            if result.get("code") == 200:
                data = result.get("data", {})
                updated_entity = entity.__class__.from_api_response(data)

                self._track_entity(updated_entity, "updated")

                return StrategyResult(
                    success=True, entity=updated_entity, raw_data=data
                )
            else:
                return StrategyResult(
                    success=False,
                    error_code=str(result.get("code")),
                    error_message=result.get("message", "API更新失败"),
                )

        except Exception as e:
            return StrategyResult(
                success=False, error_code="EXCEPTION", error_message=str(e)
            )

    def _call_update_api(self, api_module, entity: BaseEntity, updates: Dict) -> Dict:
        """调用更新API"""
        entity_name = entity.__class__.__name__
        entity_id = getattr(entity, "id")

        # 获取实体的所有字段值，并合并updates
        entity_data = entity.to_dict() if hasattr(entity, "to_dict") else {}
        entity_data.update(updates)

        method_mapping = {
            "UserEntity": ("update_user", {"user_id": entity_id, **entity_data}),
            "ReimbursementEntity": (
                "update_reimbursement",
                {"reimbursement_id": entity_id, **entity_data},
            ),
            "ProductEntity": (
                "update_product_info",
                {"product_id": entity_id, **entity_data},
            ),
            "OrderEntity": (
                "update_order_info",
                {"order_id": entity_id, **entity_data},
            ),
        }

        mapping = method_mapping.get(entity_name)
        if not mapping:
            raise ValueError(f"未找到实体 {entity_name} 的更新方法映射")

        method_name, params = mapping
        update_method = getattr(api_module, method_name)
        return update_method(**params)

    def delete(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        通过API删除实体

        @param entity_type: 实体类型
        @param entity_id: 实体ID
        @return: 策略执行结果
        """
        try:
            api_module = self._get_api_module(entity_type)

            # 调用删除API
            result = self._call_delete_api(api_module, entity_type, entity_id)

            if result.get("code") == 200:
                return StrategyResult(success=True, raw_data=result.get("data", {}))
            else:
                return StrategyResult(
                    success=False,
                    error_code=str(result.get("code")),
                    error_message=result.get("message", "API删除失败"),
                )

        except Exception as e:
            return StrategyResult(
                success=False, error_code="EXCEPTION", error_message=str(e)
            )

    def _call_delete_api(self, api_module, entity_type: Type, entity_id: Any) -> Dict:
        """调用删除API"""
        entity_name = entity_type.__name__

        method_mapping = {
            "UserEntity": ("delete_user", {"user_id": entity_id}),
            "ReimbursementEntity": (
                "delete_reimbursement",
                {"reimbursement_id": entity_id},
            ),
            "ProductEntity": ("delete_product", {"product_id": entity_id}),
            "OrderEntity": ("delete_order", {"order_id": entity_id}),
        }

        mapping = method_mapping.get(entity_name)
        if not mapping:
            raise ValueError(f"未找到实体 {entity_name} 的删除方法映射")

        method_name, params = mapping
        delete_method = getattr(api_module, method_name)
        return delete_method(**params)

    def get_by_id(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        通过API根据ID获取实体

        @param entity_type: 实体类型
        @param entity_id: 实体ID
        @return: 策略执行结果
        """
        try:
            api_module = self._get_api_module(entity_type)

            # 调用查询API
            result = self._call_get_api(api_module, entity_type, entity_id)

            if result.get("code") == 200:
                data = result.get("data", {})
                entity = entity_type.from_api_response(data)

                return StrategyResult(success=True, entity=entity, raw_data=data)
            else:
                return StrategyResult(
                    success=False,
                    error_code=str(result.get("code")),
                    error_message=result.get("message", "API查询失败"),
                )

        except Exception as e:
            return StrategyResult(
                success=False, error_code="EXCEPTION", error_message=str(e)
            )

    def _call_get_api(self, api_module, entity_type: Type, entity_id: Any) -> Dict:
        """调用查询API"""
        entity_name = entity_type.__name__

        method_mapping = {
            "UserEntity": ("get_user_by_id", {"user_id": entity_id}),
            "ReimbursementEntity": (
                "get_reimbursement_by_id",
                {"reimbursement_id": entity_id},
            ),
            "ProductEntity": ("get_product_by_id", {"product_id": entity_id}),
            "OrderEntity": ("get_order_by_id", {"order_id": entity_id}),
        }

        mapping = method_mapping.get(entity_name)
        if not mapping:
            raise ValueError(f"未找到实体 {entity_name} 的查询方法映射")

        method_name, params = mapping
        get_method = getattr(api_module, method_name)
        return get_method(**params)
