# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 变体矩阵 - 笛卡尔积自动生成用例
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
变体矩阵（Variant Matrix）

支持笛卡尔积自动生成测试用例，自动过滤无效组合，生成预期结果。

核心概念：
- Dimension（维度）：测试参数的取值范围
- Variant（变体）：一组参数的具体取值组合
- Constraint（约束）：过滤无效组合的规则
- Expected Result（预期结果）：自动生成或自定义

使用示例：
    from auto_test.demo_project.data_factory.scenarios import VariantMatrix, Dimension
    
    # 定义维度
    dimensions = [
        Dimension("role", ["admin", "user", "guest"]),
        Dimension("status", ["active", "locked"]),
        Dimension("action", ["read", "write", "delete"])
    ]
    
    # 定义约束（过滤无效组合）
    constraints = [
        lambda v: not (v["role"] == "guest" and v["action"] == "delete"),
        lambda v: not (v["status"] == "locked" and v["action"] == "write")
    ]
    
    # 创建变体矩阵
    matrix = VariantMatrix(dimensions, constraints)
    
    # 生成所有有效变体
    variants = matrix.generate()
    print(f"生成 {len(variants)} 个测试用例")
    
    # 执行变体
    for variant in variants:
        result = variant.execute()
        print(f"{variant.name}: {result.success}")
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import product
from typing import List, Dict, Any, Callable, Optional, Iterator


class VariantStatus(Enum):
    """变体状态"""
    PENDING = auto()  # 待执行
    RUNNING = auto()  # 执行中
    PASSED = auto()  # 通过
    FAILED = auto()  # 失败
    SKIPPED = auto()  # 跳过
    ERROR = auto()  # 错误


@dataclass
class Dimension:
    """
    维度定义
    
    表示一个测试参数的取值范围
    
    示例：
        Dimension("role", ["admin", "user", "guest"])
        Dimension("amount", [100, 1000, 10000])
    """
    name: str  # 维度名称
    values: List[Any]  # 取值列表
    description: str = ""  # 描述
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
    """
    变体（测试用例）
    
    一组参数的具体取值组合
    
    示例：
        Variant(
            name="role=admin_status=active_action=read",
            values={"role": "admin", "status": "active", "action": "read"},
            index=0
        )
    """
    name: str  # 变体名称
    values: Dict[str, Any]  # 参数取值
    index: int  # 变体索引
    status: VariantStatus = field(default=VariantStatus.PENDING)
    expected_result: Optional[Dict] = None
    actual_result: Optional[Any] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            # 自动生成名称
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
    total: int  # 总变体数
    passed: int = 0  # 通过数
    failed: int = 0  # 失败数
    skipped: int = 0  # 跳过数
    errors: int = 0  # 错误数
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
    """
    变体矩阵
    
    支持笛卡尔积生成测试用例，自动过滤无效组合
    
    使用示例：
        matrix = VariantMatrix(
            dimensions=[
                Dimension("role", ["admin", "user"]),
                Dimension("action", ["read", "write"])
            ],
            constraints=[
                lambda v: not (v["role"] == "user" and v["action"] == "write")
            ]
        )
        
        variants = matrix.generate()
        for variant in variants:
            print(f"执行: {variant.name}")
    """

    def __init__(
            self,
            dimensions: List[Dimension],
            constraints: Optional[List[Callable[[Dict], bool]]] = None,
            name: str = "",
            description: str = ""
    ):
        """
        初始化变体矩阵
        
        @param dimensions: 维度列表
        @param constraints: 约束函数列表（返回False表示过滤掉）
        @param name: 矩阵名称
        @param description: 描述
        """
        self.dimensions = dimensions
        self.constraints = constraints or []
        self.name = name or "VariantMatrix"
        self.description = description
        self._variants: Optional[List[Variant]] = None

    def generate(self) -> List[Variant]:
        """
        生成所有有效变体
        
        @return: 变体列表
        """
        if self._variants is not None:
            return self._variants

        # 获取所有维度的取值
        dimension_values = [d.values for d in self.dimensions]
        dimension_names = [d.name for d in self.dimensions]

        # 笛卡尔积生成所有组合
        all_combinations = list(product(*dimension_values))

        variants = []
        index = 0

        for combination in all_combinations:
            # 构建变体值字典
            values = dict(zip(dimension_names, combination))

            # 应用约束过滤
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
        """
        检查变体是否有效（通过所有约束）
        
        @param values: 变体值字典
        @return: 是否有效
        """
        for constraint in self.constraints:
            try:
                if not constraint(values):
                    return False
            except Exception:
                # 约束执行出错，视为无效
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

        # 估算（考虑约束过滤）
        total = 1
        for dim in self.dimensions:
            total *= len(dim)

        # 实际数量可能更少（因为有过滤）
        return total

    def get_dimension_names(self) -> List[str]:
        """获取所有维度名称"""
        return [d.name for d in self.dimensions]

    def add_constraint(self, constraint: Callable[[Dict], bool]):
        """添加约束"""
        self.constraints.append(constraint)
        # 重置缓存
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

        # 如果已执行，添加执行统计
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


class VariantExecutor:
    """
    变体执行器
    
    执行变体矩阵中的所有变体
    
    使用示例：
        def test_login(variant: Variant):
            # 执行测试逻辑
            user = UserEntity(role=variant["role"], status=variant["status"])
            result = user.login()
            return result.success
        
        executor = VariantExecutor(matrix)
        result = executor.execute(test_login)
    """

    def __init__(
            self,
            matrix: VariantMatrix,
            continue_on_failure: bool = True,
            max_workers: Optional[int] = None
    ):
        """
        初始化执行器
        
        @param matrix: 变体矩阵
        @param continue_on_failure: 失败时是否继续
        @param max_workers: 最大并行 workers（None表示串行）
        """
        self.matrix = matrix
        self.continue_on_failure = continue_on_failure
        self.max_workers = max_workers

    def execute(
            self,
            test_func: Callable[[Variant], bool],
            expected_result_func: Optional[Callable[[Variant], Dict]] = None
    ) -> VariantMatrixResult:
        """
        执行所有变体
        
        @param test_func: 测试函数（接收Variant，返回bool）
        @param expected_result_func: 预期结果生成函数（可选）
        @return: 执行结果
        """
        import time

        start_time = time.time()
        variants = self.matrix.generate()

        result = VariantMatrixResult(total=len(variants))

        for variant in variants:
            # 生成预期结果
            if expected_result_func:
                variant.expected_result = expected_result_func(variant)

            # 执行变体
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
        """
        带上下文的执行
        
        @param test_func: 测试函数（接收Variant和context）
        @param context: 执行上下文
        @param expected_result_func: 预期结果生成函数
        @return: 执行结果
        """

        def wrapper(variant: Variant) -> bool:
            return test_func(variant, context)

        def expected_wrapper(variant: Variant) -> Dict:
            if expected_result_func:
                return expected_result_func(variant, context)
            return {}

        return self.execute(wrapper, expected_wrapper if expected_result_func else None)


def cartesian_product(*lists: List[Any]) -> List[tuple]:
    """
    笛卡尔积工具函数
    
    @param lists: 多个列表
    @return: 笛卡尔积结果
    
    示例：
        cartesian_product([1, 2], ['a', 'b']) 
        # [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
    """
    return list(product(*lists))


def filter_variants(
        variants: List[Variant],
        predicate: Callable[[Variant], bool]
) -> List[Variant]:
    """
    过滤变体
    
    @param variants: 变体列表
    @param predicate: 过滤条件
    @return: 过滤后的变体列表
    """
    return [v for v in variants if predicate(v)]


def group_variants(
        variants: List[Variant],
        key_func: Callable[[Variant], str]
) -> Dict[str, List[Variant]]:
    """
    按指定key分组变体
    
    @param variants: 变体列表
    @param key_func: 分组key函数
    @return: 分组结果
    """
    groups = {}
    for variant in variants:
        key = key_func(variant)
        if key not in groups:
            groups[key] = []
        groups[key].append(variant)
    return groups
