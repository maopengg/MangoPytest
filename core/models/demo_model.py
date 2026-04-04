# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: demo_project 项目专用数据模型
# @Time   : 2026-04-04
# @Author : 毛鹏
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from itertools import product
from typing import Dict, List, Optional, Any, Callable, Iterator

from core.enums.demo_enum import (
    CreateStrategy, Environment, LineageNodeType, LineageRelation, VariantStatus
)


# ==================== Config Models ====================

@dataclass
class BaseConfig:
    """基础配置"""
    ENV: Environment = Environment.TEST
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = False
    ENABLE_LINEAGE: bool = True
    HOST: str = "http://localhost:8003"
    TIMEOUT: int = 30
    DEBUG: bool = False
    VERBOSE: bool = False
    EXTRA: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DevConfig(BaseConfig):
    """开发环境配置"""
    ENV: Environment = Environment.DEV
    DEBUG: bool = True
    VERBOSE: bool = True
    HOST: str = "http://localhost:8003"
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.MOCK


@dataclass
class TestConfig(BaseConfig):
    """测试环境配置"""
    ENV: Environment = Environment.TEST
    DEBUG: bool = True
    HOST: str = "http://43.142.161.61:8003/"
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class PreConfig(BaseConfig):
    """预发环境配置"""
    ENV: Environment = Environment.PRE
    DEBUG: bool = False
    HOST: str = "http://43.142.161.61:8003/"
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class ProdConfig(BaseConfig):
    """生产环境配置"""
    ENV: Environment = Environment.PROD
    DEBUG: bool = False
    HOST: str = "http://43.142.161.61:8003/"
    AUTO_CLEANUP: bool = False
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class CIConfig(BaseConfig):
    """CI/CD环境配置"""
    ENV: Environment = Environment.CI
    DEBUG: bool = False
    VERBOSE: bool = True
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.DB_ONLY
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = True
    PARALLEL: bool = True
    MAX_WORKERS: int = 4


# ==================== Strategy Models ====================

@dataclass
class StrategyResult:
    """策略执行结果"""
    success: bool
    entity: Optional[Any] = None
    entities: Optional[List[Any]] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """获取原始数据"""
        return self.raw_data

    def get_entity(self) -> Optional[Any]:
        """获取单个实体"""
        return self.entity

    def get_entities(self) -> List[Any]:
        """获取实体列表"""
        return self.entities or []


# ==================== Builder Models ====================

@dataclass
class BuilderContext:
    """Builder执行上下文"""

    def __init__(
            self,
            strategy: Optional[Any] = None,
            cascade_cleanup: bool = False,
            auto_prepare_deps: bool = True
    ):
        self.strategy = strategy
        self.cascade_cleanup = cascade_cleanup
        self.auto_prepare_deps = auto_prepare_deps
        self._created_entities: Dict[str, List[tuple]] = {}
        self._resolved_deps: Dict[str, Any] = {}
        self._builder_registry: Dict[str, Any] = {}

    def track(self, entity_type: str, entity_id: Any, builder: Any):
        """追踪创建的实体"""
        if entity_type not in self._created_entities:
            self._created_entities[entity_type] = []
        self._created_entities[entity_type].append((entity_id, builder))

    def get_resolved_dep(self, dep_type: str) -> Optional[Any]:
        """获取已解决的依赖"""
        return self._resolved_deps.get(dep_type)

    def set_resolved_dep(self, dep_type: str, entity: Any):
        """设置已解决的依赖"""
        self._resolved_deps[dep_type] = entity

    def register_builder(self, builder_type: str, builder: Any):
        """注册Builder"""
        self._builder_registry[builder_type] = builder

    def get_builder(self, builder_type: str) -> Optional[Any]:
        """获取已注册的Builder"""
        return self._builder_registry.get(builder_type)

    def get_all_created(self) -> Dict[str, List[tuple]]:
        """获取所有创建的实体"""
        return self._created_entities.copy()


# ==================== Lineage Models ====================

@dataclass
class LineageEdge:
    """血缘边 - 表示两个节点之间的关系"""
    source_id: str
    target_id: str
    relation: LineageRelation
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DataLineageNode:
    """血缘节点 - 表示数据血缘图中的一个实体"""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_type: LineageNodeType = LineageNodeType.ENTITY
    entity_type: str = ""
    entity_id: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    lifecycle: str = "active"
    incoming_edges: List[str] = field(default_factory=list)
    outgoing_edges: List[str] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if not self.entity_id and self.metadata.get("id"):
            self.entity_id = str(self.metadata.get("id"))

    def add_incoming_edge(self, edge_id: str):
        """添加入边"""
        if edge_id not in self.incoming_edges:
            self.incoming_edges.append(edge_id)
            self.updated_at = datetime.now()

    def add_outgoing_edge(self, edge_id: str):
        """添加出边"""
        if edge_id not in self.outgoing_edges:
            self.outgoing_edges.append(edge_id)
            self.updated_at = datetime.now()

    def get_full_id(self) -> str:
        """获取完整标识"""
        return f"{self.entity_type}:{self.entity_id}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.name,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "lifecycle": self.lifecycle,
            "incoming_edges": self.incoming_edges,
            "outgoing_edges": self.outgoing_edges,
        }

    @classmethod
    def from_entity(
            cls,
            entity_type: str,
            entity_id: str,
            source: str = "",
            metadata: Optional[Dict[str, Any]] = None,
            node_type: LineageNodeType = LineageNodeType.ENTITY
    ) -> "DataLineageNode":
        """从实体创建血缘节点"""
        return cls(
            node_type=node_type,
            entity_type=entity_type,
            entity_id=entity_id,
            source=source,
            metadata=metadata or {},
        )


@dataclass
class LineagePath:
    """血缘路径 - 表示从一个节点到另一个节点的完整路径"""
    nodes: List[DataLineageNode] = field(default_factory=list)
    edges: List[LineageEdge] = field(default_factory=list)
    path_type: str = "unknown"

    def __len__(self) -> int:
        """路径长度（边数）"""
        return len(self.edges)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "path_type": self.path_type,
            "length": len(self),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }


# ==================== Variant Matrix Models ====================

@dataclass
class Dimension:
    """维度定义 - 表示一个测试参数的取值范围"""
    name: str
    values: List[Any]
    description: str = ""
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.values:
            raise ValueError(f"维度 {self.name} 必须至少有一个取值")

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)


@dataclass
class Variant:
    """变体（测试用例）- 一组参数的具体取值组合"""
    name: str
    values: Dict[str, Any]
    index: int
    status: VariantStatus = field(default=VariantStatus.PENDING)
    expected_result: Optional[Dict] = None
    actual_result: Optional[Any] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            parts = [f"{k}={v}" for k, v in self.values.items()]
            self.name = "_".join(parts)

    def get(self, key: str, default=None):
        """获取参数值"""
        return self.values.get(key, default)

    def __getitem__(self, key: str):
        return self.values[key]

    def __contains__(self, key: str):
        return key in self.values

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "values": self.values,
            "index": self.index,
            "status": self.status.name,
            "expected_result": self.expected_result,
            "execution_time": self.execution_time,
            "error_message": self.error_message
        }


@dataclass
class VariantMatrixResult:
    """变体矩阵执行结果"""
    total: int
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    variants: List[Variant] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total == 0:
            return 0.0
        return self.passed / self.total

    def get_failed_variants(self) -> List[Variant]:
        """获取失败的变体"""
        return [v for v in self.variants if v.status == VariantStatus.FAILED]

    def get_passed_variants(self) -> List[Variant]:
        """获取通过的变体"""
        return [v for v in self.variants if v.status == VariantStatus.PASSED]


class VariantMatrix:
    """变体矩阵 - 支持笛卡尔积生成测试用例，自动过滤无效组合"""

    def __init__(
            self,
            dimensions: List[Dimension],
            constraints: Optional[List[Callable[[Dict], bool]]] = None,
            name: str = "",
            description: str = ""
    ):
        self.dimensions = dimensions
        self.constraints = constraints or []
        self.name = name or "VariantMatrix"
        self.description = description
        self._variants: Optional[List[Variant]] = None

    def generate(self) -> List[Variant]:
        """生成所有有效变体"""
        if self._variants is not None:
            return self._variants

        dimension_values = [d.values for d in self.dimensions]
        dimension_names = [d.name for d in self.dimensions]
        all_combinations = list(product(*dimension_values))

        variants = []
        index = 0

        for combination in all_combinations:
            values = dict(zip(dimension_names, combination))
            if self._is_valid(values):
                variant = Variant(
                    name=self._generate_variant_name(values),
                    values=values,
                    index=index
                )
                variants.append(variant)
                index += 1

        self._variants = variants
        return variants

    def _is_valid(self, values: Dict) -> bool:
        """检查变体是否有效（通过所有约束）"""
        for constraint in self.constraints:
            try:
                if not constraint(values):
                    return False
            except Exception:
                return False
        return True

    def _generate_variant_name(self, values: Dict) -> str:
        """生成变体名称"""
        parts = [f"{k}={v}" for k, v in values.items()]
        return "_".join(parts)

    def get_variant_count(self) -> int:
        """获取变体数量（不生成）"""
        if self._variants is not None:
            return len(self._variants)
        total = 1
        for dim in self.dimensions:
            total *= len(dim)
        return total

    def get_dimension_names(self) -> List[str]:
        """获取所有维度名称"""
        return [d.name for d in self.dimensions]

    def add_constraint(self, constraint: Callable[[Dict], bool]):
        """添加约束"""
        self.constraints.append(constraint)
        self._variants = None

    def remove_constraint(self, constraint: Callable[[Dict], bool]):
        """移除约束"""
        if constraint in self.constraints:
            self.constraints.remove(constraint)
            self._variants = None

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        variants = self.generate()
        stats = {
            "total_variants": len(variants),
            "dimensions": len(self.dimensions),
            "constraints": len(self.constraints),
            "dimension_details": {d.name: len(d) for d in self.dimensions}
        }
        status_counts = {}
        for v in variants:
            status_name = v.status.name
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        if status_counts:
            stats["execution"] = status_counts
        return stats

    def __iter__(self) -> Iterator[Variant]:
        """迭代器"""
        return iter(self.generate())

    def __len__(self) -> int:
        """变体数量"""
        return len(self.generate())

    def __getitem__(self, index: int) -> Variant:
        """获取指定索引的变体"""
        variants = self.generate()
        return variants[index]


@dataclass
class VariantExecutor:
    """变体执行器 - 执行变体矩阵中的所有变体"""

    def __init__(
            self,
            matrix: VariantMatrix,
            continue_on_failure: bool = True,
            max_workers: Optional[int] = None
    ):
        self.matrix = matrix
        self.continue_on_failure = continue_on_failure
        self.max_workers = max_workers

    def execute(
            self,
            test_func: Callable[[Variant], bool],
            expected_result_func: Optional[Callable[[Variant], Dict]] = None
    ) -> VariantMatrixResult:
        """执行所有变体"""
        import time

        start_time = time.time()
        variants = self.matrix.generate()
        result = VariantMatrixResult(total=len(variants))

        for variant in variants:
            if expected_result_func:
                variant.expected_result = expected_result_func(variant)

            variant.status = VariantStatus.RUNNING
            variant_start = time.time()

            try:
                success = test_func(variant)
                variant.execution_time = time.time() - variant_start

                if success:
                    variant.status = VariantStatus.PASSED
                    result.passed += 1
                else:
                    variant.status = VariantStatus.FAILED
                    result.failed += 1
                    if not self.continue_on_failure:
                        break

            except Exception as e:
                variant.status = VariantStatus.ERROR
                variant.error_message = str(e)
                variant.execution_time = time.time() - variant_start
                result.errors += 1
                if not self.continue_on_failure:
                    break

        result.execution_time = time.time() - start_time
        result.variants = variants
        return result

    def execute_with_context(
            self,
            test_func: Callable[[Variant, Any], bool],
            context: Any,
            expected_result_func: Optional[Callable[[Variant, Any], Dict]] = None
    ) -> VariantMatrixResult:
        """带上下文的执行"""

        def wrapper(variant: Variant) -> bool:
            return test_func(variant, context)

        def expected_wrapper(variant: Variant) -> Dict:
            if expected_result_func:
                return expected_result_func(variant, context)
            return {}

        return self.execute(wrapper, expected_wrapper if expected_result_func else None)


# ==================== Settings Manager ====================

class Settings:
    """配置管理器（单例）"""

    _instance: Optional['Settings'] = None
    _config: Optional[BaseConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置"""
        env = self._detect_environment()

        config_map = {
            Environment.DEV: DevConfig(),
            Environment.TEST: TestConfig(),
            Environment.PRE: PreConfig(),
            Environment.PROD: ProdConfig(),
            Environment.CI: CIConfig(),
        }
        self._config = config_map.get(env, TestConfig())

    def _detect_environment(self) -> Environment:
        """检测运行环境"""
        import os
        env_str = os.environ.get("ENV", "test").lower()

        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            return Environment.CI

        env_map = {
            "dev": Environment.DEV,
            "development": Environment.DEV,
            "test": Environment.TEST,
            "testing": Environment.TEST,
            "pre": Environment.PRE,
            "staging": Environment.PRE,
            "prod": Environment.PROD,
            "production": Environment.PROD,
            "ci": Environment.CI,
        }
        return env_map.get(env_str, Environment.TEST)

    @property
    def config(self) -> BaseConfig:
        """获取当前配置"""
        return self._config

    def reload(self):
        """重新加载配置"""
        self._load_config()

    def update(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    @property
    def ENV(self) -> Environment:
        return self._config.ENV

    @property
    def DEFAULT_STRATEGY(self) -> CreateStrategy:
        return self._config.DEFAULT_STRATEGY

    @property
    def AUTO_CLEANUP(self) -> bool:
        return self._config.AUTO_CLEANUP

    @property
    def CASCADE_CLEANUP(self) -> bool:
        return self._config.CASCADE_CLEANUP

    @property
    def ENABLE_LINEAGE(self) -> bool:
        return self._config.ENABLE_LINEAGE

    @property
    def HOST(self) -> str:
        return self._config.HOST

    @property
    def DEBUG(self) -> bool:
        return self._config.DEBUG


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
