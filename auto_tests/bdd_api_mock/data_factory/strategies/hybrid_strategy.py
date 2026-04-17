# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Hybrid策略 - API头+DB明细（复杂对象）
# @Time   : 2026-04-01
# @Author : 毛鹏
from typing import Type, Optional, Dict, Any, TypeVar

from core.base import BaseEntity, BaseStrategy, StrategyResult


T = TypeVar("T", bound=BaseEntity)


class HybridStrategy(BaseStrategy[T]):
    """
    Hybrid策略 - API创建头信息 + DB插入明细（复杂对象）
    
    结合API和DB的优势：
    - 使用API创建主对象（触发业务规则验证）
    - 使用DB插入关联明细（批量、快速）
    
    适用于：复杂对象（订单+明细、报销+发票）、大数据量关联
    
    特点：
    - 平衡可靠性和性能
    - 主对象走API（业务规则）
    - 明细走DB（批量速度）
    
    注意：此策略需要API和DB双重配置，当前为占位实现
    
    使用示例：
        # 创建复杂对象：报销单 + 100张发票明细
        strategy = HybridStrategy(
            api_token="xxx",
            db_config={...}
        )
        
        result = strategy.create(
            ReimbursementWithInvoices,
            header={"user_id": 1, "amount": 10000},
            details=[{"invoice_no": f"INV_{i}", "amount": 100} for i in range(100)]
        )
    """

    def __init__(
            self,
            api_token: Optional[str] = None,
            db_config: Optional[Dict] = None,
            context: Optional[Any] = None,
            config: Optional[Dict] = None
    ):
        """
        初始化Hybrid策略
        
        @param api_token: API认证token
        @param db_config: 数据库连接配置
        @param context: 执行上下文
        @param config: 策略配置
        """
        super().__init__(context, config)
        self.api_token = api_token
        self.db_config = db_config or {}

        # 初始化子策略
        from .api_strategy import APIStrategy
        from .db_strategy import DBStrategy

        self._api_strategy = APIStrategy(token=api_token, context=context, config=config)
        self._db_strategy = DBStrategy(db_config=db_config, context=context, config=config)

    def create(self, entity_type: Type[T], **kwargs) -> StrategyResult:
        """
        混合创建实体
        
        @param entity_type: 实体类型
        @param kwargs: 必须包含 header 和 details
            - header: 主对象数据（走API）
            - details: 明细数据列表（走DB）
        @return: 策略执行结果
        """
        try:
            header_data = kwargs.get("header", {})
            details_data = kwargs.get("details", [])

            # 步骤1：使用API创建主对象
            header_result = self._api_strategy.create(entity_type, **header_data)

            if not header_result.success:
                return StrategyResult(
                    success=False,
                    error_code="HEADER_CREATE_FAILED",
                    error_message=f"主对象创建失败: {header_result.error_message}"
                )

            header_entity = header_result.entity
            header_id = getattr(header_entity, "id", None)

            # 步骤2：使用DB批量插入明细
            if details_data:
                # 为每个明细添加外键关联
                for detail in details_data:
                    detail["parent_id"] = header_id

                # 这里假设有对应的明细实体类型
                # 实际项目中需要传入明细实体类型
                details_result = self._db_strategy.batch_create(
                    entity_type,  # 简化处理，实际应该用明细实体类型
                    details_data
                )

                if not details_result.success:
                    # 回滚：删除已创建的主对象
                    self._api_strategy.delete(entity_type, header_id)

                    return StrategyResult(
                        success=False,
                        error_code="DETAILS_CREATE_FAILED",
                        error_message=f"明细创建失败: {details_result.error_message}"
                    )

                details_entities = details_result.entities
            else:
                details_entities = []

            # 组装结果
            return StrategyResult(
                success=True,
                entity=header_entity,
                raw_data={
                    "header": header_entity.__dict__ if hasattr(header_entity, "__dict__") else {},
                    "details_count": len(details_entities),
                    "details": [e.__dict__ for e in details_entities] if details_entities else []
                },
                metadata={
                    "strategy": "hybrid",
                    "header_id": header_id,
                    "details_count": len(details_entities)
                }
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )

    def update(self, entity: T, **kwargs) -> StrategyResult:
        """
        混合更新实体
        
        主对象走API更新，明细走DB更新
        """
        try:
            # 简化实现：分别调用API和DB策略
            header_updates = kwargs.get("header", {})
            details_updates = kwargs.get("details", [])

            # 更新主对象
            if header_updates:
                result = self._api_strategy.update(entity, **header_updates)
                if not result.success:
                    return result

            return StrategyResult(
                success=True,
                entity=entity,
                metadata={"strategy": "hybrid", "action": "update"}
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )

    def delete(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        混合删除实体
        
        先删除DB明细，再删除API主对象
        """
        try:
            # 步骤1：删除明细（DB）
            # 实际项目中需要先查询明细ID列表
            # self._db_strategy.batch_delete(detail_type, detail_ids)

            # 步骤2：删除主对象（API）
            result = self._api_strategy.delete(entity_type, entity_id)

            return StrategyResult(
                success=result.success,
                error_code=result.error_code,
                error_message=result.error_message,
                metadata={"strategy": "hybrid", "action": "delete"}
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )

    def get_by_id(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """
        混合查询实体
        
        主对象走API查询，明细走DB查询
        """
        try:
            # 查询主对象
            header_result = self._api_strategy.get_by_id(entity_type, entity_id)

            if not header_result.success:
                return header_result

            # 查询明细（实际项目中需要）
            # details_result = self._db_strategy.query(...)

            return StrategyResult(
                success=True,
                entity=header_result.entity,
                raw_data=header_result.raw_data,
                metadata={"strategy": "hybrid", "action": "get"}
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )
