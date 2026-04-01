# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景基类 - 业务流程封装（增强版）
# @Time   : 2026-03-31
# @Author : 毛鹏
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic, Type, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import copy
import sys
import os

# 添加父目录到路径以确保导入工作
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from entities.base_entity import BaseEntity
    from context import Context
    from scenarios.variant_matrix import VariantMatrix
except ImportError:
    # 回退到相对导入
    try:
        from ..entities.base_entity import BaseEntity
        from ..context import Context
        from .variant_matrix import VariantMatrix
    except ImportError:
        # 如果都失败，使用延迟导入
        BaseEntity = None
        Context = None
        VariantMatrix = None


T = TypeVar("T", bound=BaseEntity if BaseEntity else object)


@dataclass
class ScenarioResult:
    """场景执行结果"""

    success: bool = True
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    entities: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    context: Optional[Any] = None  # 执行上下文
    variant_name: Optional[str] = None  # 变体名称
    expected: Dict[str, Any] = field(default_factory=dict)  # 【新增】预期结果
    actual: Dict[str, Any] = field(default_factory=dict)  # 【新增】实际结果

    def add_entity(self, name: str, entity: Any):
        """添加实体到结果"""
        self.entities[name] = entity

    def get_entity(self, name: str) -> Optional[Any]:
        """获取实体"""
        return self.entities.get(name)

    def add_error(self, error: str):
        """添加错误信息"""
        self.success = False
        self.errors.append(error)
        self.message = error if not self.message else f"{self.message}; {error}"

    def set_expected(self, key: str, value: Any):
        """【新增】设置预期结果"""
        self.expected[key] = value

    def set_actual(self, key: str, value: Any):
        """【新增】设置实际结果"""
        self.actual[key] = value

    def is_match(self) -> bool:
        """【新增】检查预期与实际是否匹配"""
        for key, expected_value in self.expected.items():
            if key in self.actual:
                if self.actual[key] != expected_value:
                    return False
        return True


# 依赖声明类型
DependencyType = Type[Any]
Dependencies = List[DependencyType]

# 【新增】创建实体声明类型
CreatesType = Type[Any]
Creates = List[CreatesType]


class BaseScenario(ABC, Generic[T]):
    """
    场景基类 - 增强版

    职责：
    1. 封装业务流程（多个步骤的组合）
    2. 管理实体间的依赖关系（依赖声明自动解决）
    3. 支持变体矩阵参数化
    4. 提供业务编排能力
    5. 提供场景执行结果
    6. 【新增】声明创建的实体
    7. 【新增】预期结果验证

    使用示例：
        class LoginScenario(BaseScenario):
            # 依赖声明
            requires: Dependencies = [User]
            
            # 【新增】创建声明
            creates: Creates = [LoginLog, Session]

            # 变体矩阵
            variants = VariantMatrix([
                Dimension("actor", [...]),
                Dimension("credential", [...]),
            ])

            def orchestrate(self, ctx: Context):
                # 业务编排
                user = ctx.use(User, role="employee")
                ctx.action(user.login, password="123456")
                ctx.expect(user.status).equals("active")
    """

    # 类属性：依赖声明
    requires: Dependencies = []

    # 【新增】类属性：创建声明 - 声明场景会创建哪些实体
    creates: Creates = []

    # 类属性：变体矩阵
    variants: Optional[Any] = None

    # 类属性：场景参数定义
    params_schema: Dict[str, Any] = {}

    def __init__(
        self,
        token: str = None,
        factory=None,
        auto_resolve_deps: bool = True,
        context: Optional[Any] = None,
        **params
    ):
        """
        初始化场景

        @param token: 认证token
        @param factory: 数据工厂实例
        @param auto_resolve_deps: 是否自动解决依赖
        @param context: 外部传入的上下文（可选）
        @param params: 【新增】场景参数
        """
        self.token = token
        self.factory = factory
        self.auto_resolve_deps = auto_resolve_deps
        self._created_entities: List[Any] = []
        self._resolved_deps: Dict[str, Any] = {}
        self._params: Dict[str, Any] = params  # 【新增】场景参数

        # 延迟导入 Context
        if context is None:
            try:
                from context import Context
                self.context = Context(
                    auto_cleanup=True, cascade_cleanup=False, enable_lineage=True
                )
            except ImportError:
                self.context = None
        else:
            self.context = context

        # 变体相关
        self._current_variant: Optional[Dict[str, Any]] = None
        self._variant_name: Optional[str] = None

    @property
    def params(self) -> Dict[str, Any]:
        """【新增】获取场景参数"""
        return self._params

    def set_params(self, **params):
        """【新增】设置场景参数"""
        self._params.update(params)

    @abstractmethod
    def orchestrate(self, ctx: Any) -> ScenarioResult:
        """
        业务编排 - 子类必须实现

        使用 ctx 进行：
        - ctx.create() - 创建实体
        - ctx.use() - 复用实体
        - ctx.action() - 执行业务动作
        - ctx.expect() - 验证预期
        - ctx.event() - 验证事件

        @param ctx: 场景上下文
        @return: 场景执行结果
        """
        pass

    def execute(self, *args, **kwargs) -> ScenarioResult:
        """
        执行场景（完整生命周期）

        1. 前置检查
        2. 解决依赖
        3. 执行业务编排
        4. 后置处理
        5. 【新增】验证结果

        @return: 场景执行结果
        """
        # 前置检查
        if not self.pre_execute(*args, **kwargs):
            return ScenarioResult(
                success=False, message="前置检查失败", context=self.context
            )

        try:
            # 解决依赖
            if self.auto_resolve_deps:
                self._resolve_dependencies()

            # 执行业务编排
            result = self.orchestrate(self.context)
            result.context = self.context
            result.variant_name = self._variant_name

            # 【新增】自动验证结果
            if not self.validate_result(result):
                result.success = False
                if not result.message:
                    result.message = "结果验证失败"

        except Exception as e:
            result = ScenarioResult(
                success=False, message=f"场景执行异常: {str(e)}", context=self.context
            )

        # 后置处理
        self.post_execute(result)

        return result

    def run(self, *args, **kwargs) -> ScenarioResult:
        """运行场景（execute 的别名）"""
        return self.execute(*args, **kwargs)

    def pre_execute(self, *args, **kwargs) -> bool:
        """
        执行前准备

        子类可重写此方法进行前置检查

        @return: 是否继续执行
        """
        return True

    def post_execute(self, result: ScenarioResult):
        """
        执行后处理

        子类可重写此方法进行后置处理

        @param result: 执行结果
        """
        pass

    def _resolve_dependencies(self):
        """
        解决依赖声明

        根据 requires 列表自动创建或获取依赖实体
        """
        for dep_class in self.requires:
            dep_name = dep_class.__name__.lower().replace("entity", "")

            # 尝试从上下文中获取
            if self.context:
                existing = self.context.use(dep_class)
                if existing:
                    self._resolved_deps[dep_name] = existing
                    continue

            # 尝试使用智能工厂方法创建
            entity = self._create_dependency_entity(dep_class)
            if entity:
                self._resolved_deps[dep_name] = entity
                if self.context:
                    self.context.create(dep_class, **self._entity_to_kwargs(entity))

    def _create_dependency_entity(
        self, entity_class: Type[Any]
    ) -> Optional[Any]:
        """
        使用智能工厂方法创建依赖实体

        @param entity_class: 实体类
        @return: 创建的实体或 None
        """
        # 尝试调用 random() 方法
        if hasattr(entity_class, "random") and callable(
            getattr(entity_class, "random")
        ):
            try:
                return entity_class.random()
            except Exception:
                pass

        # 尝试调用默认构造
        try:
            return entity_class()
        except Exception:
            pass

        return None

    def _entity_to_kwargs(self, entity: Any) -> Dict[str, Any]:
        """将实体转换为 kwargs"""
        if hasattr(entity, "__dict__"):
            return {k: v for k, v in entity.__dict__.items() if not k.startswith("_")}
        return {}

    def get_dependency(self, name: str) -> Optional[Any]:
        """
        获取已解决的依赖

        @param name: 依赖名称
        @return: 依赖实体
        """
        return self._resolved_deps.get(name)

    def set_variant(self, variant_name: str, variant_data: Dict[str, Any]):
        """
        设置当前变体

        @param variant_name: 变体名称
        @param variant_data: 变体数据
        """
        self._variant_name = variant_name
        self._current_variant = variant_data
        
        # 【新增】将变体参数合并到场景参数
        if variant_data:
            for key, value in variant_data.items():
                if hasattr(value, 'values'):
                    self._params.update(value.values)
                elif isinstance(value, dict):
                    self._params.update(value)

    @classmethod
    def all_variants(cls) -> List[Any]:
        """
        获取所有变体组合

        @return: 变体列表
        """
        if cls.variants:
            return cls.variants.generate()
        return []

    @classmethod
    def variant(cls, **selections) -> Dict[str, Any]:
        """
        获取指定变体

        @param selections: 变体选择
        @return: 变体数据
        """
        if cls.variants:
            # 构建变体数据
            variant_data = {}
            for dim_name, variant_name in selections.items():
                if dim_name in cls.variants.dimensions:
                    dim = cls.variants.dimensions[dim_name]
                    if variant_name in dim.variants:
                        variant_data[dim_name] = dim.variants[variant_name]
            return variant_data
        return {}

    def _expected_result(self) -> Dict[str, Any]:
        """
        预期结果 - 子类可重写

        【增强】支持基于变体和参数动态计算预期结果

        @return: 预期结果字典
        """
        # 基础预期：成功
        expected = {"success": True}
        
        # 根据变体调整预期
        if self._current_variant:
            # 检查是否有预期的失败情况
            for dim_name, variant in self._current_variant.items():
                if hasattr(variant, 'values'):
                    values = variant.values
                    # 检查是否有错误码
                    if 'error_code' in values:
                        expected['success'] = False
                        expected['error_code'] = values['error_code']
                    # 检查是否有有效标志
                    if 'valid' in values and not values['valid']:
                        expected['success'] = False
        
        return expected

    def validate_result(self, result: ScenarioResult) -> bool:
        """
        验证结果是否符合预期

        【增强】更完善的验证逻辑

        @param result: 实际结果
        @return: 是否通过验证
        """
        expected = self._expected_result()
        
        # 设置预期和实际结果到 result
        result.expected = expected
        result.actual = {
            "success": result.success,
            **result.data
        }

        # 验证成功标志
        if "success" in expected:
            if result.success != expected["success"]:
                return False

        # 验证错误码
        if "error_code" in expected:
            actual_error = result.data.get("error_code") or result.data.get("error")
            if actual_error != expected["error_code"]:
                return False

        return True

    def register_entity(self, entity: Any):
        """
        注册创建的实体

        @param entity: 实体实例
        """
        self._created_entities.append(entity)

    def get_created_entities(self) -> List[Any]:
        """
        获取所有创建的实体

        @return: 实体列表
        """
        return self._created_entities.copy()

    def get_created_entities_by_type(self, entity_type: Type[Any]) -> List[Any]:
        """
        【新增】按类型获取创建的实体

        @param entity_type: 实体类型
        @return: 实体列表
        """
        return [e for e in self._created_entities if isinstance(e, entity_type)]

    def cleanup(self):
        """
        清理场景创建的数据
        """
        # 清理上下文
        if self.context and hasattr(self.context, 'cleanup'):
            self.context.cleanup()

        # 清理注册的实体
        for entity in reversed(self._created_entities):
            if hasattr(entity, "mark_as_deleted"):
                entity.mark_as_deleted()

        self._created_entities.clear()
        self._resolved_deps.clear()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()

    # 【新增】快捷方法
    
    @classmethod
    def execute_variant(cls, variant_name: str, **kwargs) -> ScenarioResult:
        """
        【新增】执行指定变体

        @param variant_name: 变体名称（格式：dim1=value1,dim2=value2）
        @param kwargs: 其他参数
        @return: 执行结果
        """
        # 解析变体名称
        selections = {}
        for part in variant_name.split(","):
            if "=" in part:
                dim, val = part.split("=", 1)
                selections[dim.strip()] = val.strip()
        
        # 获取变体数据
        variant_data = cls.variant(**selections)
        
        # 创建场景实例并执行
        scenario = cls(**kwargs)
        scenario.set_variant(variant_name, variant_data)
        return scenario.execute()

    @classmethod
    def execute_all_variants(cls, **kwargs) -> List[ScenarioResult]:
        """
        【新增】执行所有变体

        @param kwargs: 其他参数
        @return: 执行结果列表
        """
        results = []
        variants = cls.all_variants()
        
        for i, variant in enumerate(variants):
            scenario = cls(**kwargs)
            variant_name = f"variant_{i+1}"
            scenario.set_variant(variant_name, {"variant": variant})
            result = scenario.execute()
            results.append(result)
        
        return results
