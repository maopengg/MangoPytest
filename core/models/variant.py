# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 变体矩阵相关模型
# @Time   : 2026-05-03
# @Author : 毛鹏
from dataclasses import dataclass, field
from itertools import product
from typing import Dict, List, Optional, Any, Callable, Iterator

from core.enums.demo_enum import VariantStatus


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
