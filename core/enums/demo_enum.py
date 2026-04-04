# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: demo_project 项目专用枚举
# @Time   : 2026-04-04
# @Author : 毛鹏
from enum import Enum, auto


class CreateStrategy(Enum):
    """数据创建策略"""
    API_ONLY = "api"  # 仅API调用
    DB_ONLY = "db"  # 仅数据库操作
    HYBRID = "hybrid"  # API+DB混合
    MOCK = "mock"  # Mock数据


class Environment(Enum):
    """运行环境"""
    DEV = "dev"
    TEST = "test"
    PRE = "pre"
    PROD = "prod"
    CI = "ci"


class EntityStatus(Enum):
    """实体状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消
    DELETED = "deleted"  # 已删除


class CreateStrategyAuto(Enum):
    """创建策略枚举（auto版本）"""
    API_ONLY = auto()  # 仅API调用（默认，最可靠）
    DB_ONLY = auto()  # 仅数据库插入（批量/性能）
    HYBRID = auto()  # 混合模式（API头+DB明细）
    MOCK = auto()  # 本地Mock（单元测试）


class DependencyLevel(Enum):
    """模块依赖层级（D最低，A最高）"""
    LEVEL_D = auto()  # 基础层：Org, User
    LEVEL_C = auto()  # 业务层：Budget
    LEVEL_B = auto()  # 流程层：Reimbursement
    LEVEL_A = auto()  # 应用层：Payment


class LineageNodeType(Enum):
    """血缘节点类型"""
    ENTITY = auto()  # 业务实体（User, Order等）
    API_CALL = auto()  # API调用
    DATABASE = auto()  # 数据库操作
    FILE = auto()  # 文件操作
    EVENT = auto()  # 事件/消息
    TEST_CASE = auto()  # 测试用例
    SCENARIO = auto()  # 测试场景
    BUILDER = auto()  # 构造器


class LineageRelation(Enum):
    """血缘关系类型"""
    CREATES = "creates"  # 创建
    DEPENDS_ON = "depends_on"  # 依赖
    REFERENCES = "references"  # 引用
    TRIGGERS = "triggers"  # 触发
    CONTAINS = "contains"  # 包含
    TRANSFORMS = "transforms"  # 转换
    PRODUCES = "produces"  # 产生
    CONSUMES = "consumes"  # 消费


class ImpactLevel(Enum):
    """影响级别"""
    CRITICAL = auto()  # 关键影响（影响核心业务）
    HIGH = auto()  # 高影响（影响多个下游）
    MEDIUM = auto()  # 中等影响（影响少量下游）
    LOW = auto()  # 低影响（无下游或影响很小）


class VariantStatus(Enum):
    """变体状态"""
    PENDING = auto()  # 待执行
    RUNNING = auto()  # 执行中
    PASSED = auto()  # 通过
    FAILED = auto()  # 失败
    SKIPPED = auto()  # 跳过
    ERROR = auto()  # 错误
