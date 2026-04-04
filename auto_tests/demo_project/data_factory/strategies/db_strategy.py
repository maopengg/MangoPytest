# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: DB策略 - 直接SQL插入（批量/性能测试）
# @Time   : 2026-04-01
# @Author : 毛鹏
from typing import Type, Optional, Dict, Any, TypeVar

from core.base import BaseEntity, BaseStrategy, StrategyResult

T = TypeVar("T", bound=BaseEntity)


class DBStrategy(BaseStrategy[T]):
    """
    DB策略 - 直接操作数据库（批量/性能测试）
    
    绕过API直接操作数据库，速度最快，适合批量构造测试数据。
    适用于：性能测试、大数据量构造、数据迁移
    
    特点：
    - 极速执行（直接SQL）
    - 适合批量操作
    - 不触发业务钩子（hooks）
    - 需要数据库连接配置
    
    注意：此策略需要真实数据库连接，当前为占位实现
    
    使用示例：
        # 需要配置数据库连接
        config = {
            "host": "localhost",
            "port": 3306,
            "database": "test_db",
            "user": "root",
            "password": "password"
        }
        strategy = DBStrategy(db_config=config)
        
        # 批量创建
        users_data = [{"username": f"user_{i}", "password": "123456"} for i in range(1000)]
        result = strategy.batch_create(UserEntity, users_data)
    """

    def __init__(self, db_config: Optional[Dict] = None, context: Optional[Any] = None, config: Optional[Dict] = None):
        """
        初始化DB策略
        
        @param db_config: 数据库连接配置
        @param context: 执行上下文
        @param config: 策略配置
        """
        super().__init__(context, config)
        self.db_config = db_config or {}
        self._connection = None
        self._cursor = None

        # 表名映射
        self._table_mapping = {
            "UserEntity": "users",
            "ReimbursementEntity": "reimbursements",
            "DeptApprovalEntity": "dept_approvals",
            "FinanceApprovalEntity": "finance_approvals",
            "CEOApprovalEntity": "ceo_approvals",
        }

    def _get_table_name(self, entity_type: Type[T]) -> str:
        """获取实体对应的表名"""
        entity_name = entity_type.__name__
        return self._table_mapping.get(entity_name, entity_name.lower().replace("entity", "s"))

    def _connect(self):
        """建立数据库连接（占位实现）"""
        # 实际项目中使用 sqlalchemy 或 pymysql 等库
        # 这里为演示目的，返回模拟连接
        if not self._connection:
            # 模拟连接
            self._connection = {"connected": True, "config": self.db_config}
        return self._connection

    def create(self, entity_type: Type[T], **kwargs) -> StrategyResult:
        """
        通过SQL插入创建实体
        
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

            # 模拟SQL插入（实际项目中执行真实SQL）
            table_name = self._get_table_name(entity_type)

            # 生成ID（实际项目中由数据库自增或序列生成）
            if not getattr(entity, "id", None):
                import random
                entity.id = random.randint(10000, 99999)

            # 追踪
            self._track_entity(entity, "created")

            return StrategyResult(
                success=True,
                entity=entity,
                metadata={"strategy": "db", "table": table_name, "sql": f"INSERT INTO {table_name} ..."}
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )

    def update(self, entity: T, **kwargs) -> StrategyResult:
        """通过SQL更新实体"""
        try:
            entity_id = getattr(entity, "id", None)
            if not entity_id:
                return StrategyResult(
                    success=False,
                    error_code="NO_ENTITY_ID",
                    error_message="实体没有ID，无法更新"
                )

            table_name = self._get_table_name(entity.__class__)

            # 更新属性
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            self._track_entity(entity, "updated")

            return StrategyResult(
                success=True,
                entity=entity,
                metadata={"strategy": "db", "table": table_name, "sql": f"UPDATE {table_name} ..."}
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )

    def delete(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """通过SQL删除实体"""
        try:
            table_name = self._get_table_name(entity_type)

            return StrategyResult(
                success=True,
                metadata={"strategy": "db", "table": table_name,
                          "sql": f"DELETE FROM {table_name} WHERE id={entity_id}"}
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )

    def get_by_id(self, entity_type: Type[T], entity_id: Any) -> StrategyResult:
        """通过SQL查询实体"""
        try:
            table_name = self._get_table_name(entity_type)

            # 模拟查询结果
            return StrategyResult(
                success=False,  # 实际项目中查询数据库
                error_code="NOT_IMPLEMENTED",
                error_message=f"DB查询需要真实数据库连接（表: {table_name}）"
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )

    def batch_create(self, entity_type: Type[T], data_list: list) -> StrategyResult:
        """
        批量创建实体（DB策略的优势）
        
        @param entity_type: 实体类型
        @param data_list: 数据列表
        @return: 策略执行结果
        """
        try:
            table_name = self._get_table_name(entity_type)
            entities = []

            # 模拟批量插入
            for data in data_list:
                entity = entity_type(**data)
                if not getattr(entity, "id", None):
                    import random
                    entity.id = random.randint(10000, 99999)
                entities.append(entity)
                self._track_entity(entity, "created")

            return StrategyResult(
                success=True,
                entities=entities,
                metadata={
                    "strategy": "db",
                    "table": table_name,
                    "batch_size": len(data_list),
                    "sql": f"INSERT INTO {table_name} ... (batch)"
                }
            )

        except Exception as e:
            return StrategyResult(
                success=False,
                error_code="EXCEPTION",
                error_message=str(e)
            )
