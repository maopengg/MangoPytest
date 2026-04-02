# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态机核心实现
# @Time   : 2026-04-01
# @Author : 毛鹏
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

from .exceptions import TransitionHookError


class State:
    """状态定义"""

    def __init__(
            self,
            name: str,
            description: str = "",
            is_initial: bool = False,
            is_final: bool = False,
            metadata: Optional[Dict] = None
    ):
        """
        初始化状态
        
        @param name: 状态名称
        @param description: 状态描述
        @param is_initial: 是否为初始状态
        @param is_final: 是否为终止状态
        @param metadata: 元数据
        """
        self.name = name
        self.description = description
        self.is_initial = is_initial
        self.is_final = is_final
        self.metadata = metadata or {}

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, State):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"State({self.name})"

    def __str__(self):
        return self.name


@dataclass
class Transition:
    """状态转换定义"""
    from_state: str
    to_state: str
    event: Optional[str] = None  # 触发事件名称
    condition: Optional[Callable] = None  # 转换条件
    description: str = ""
    metadata: Dict = field(default_factory=dict)

    def can_execute(self, entity: Any, **context) -> bool:
        """检查转换是否可以执行"""
        if self.condition is None:
            return True
        try:
            return self.condition(entity, **context)
        except Exception:
            return False


@dataclass
class TransitionResult:
    """状态转换结果"""
    success: bool
    from_state: str
    to_state: str
    entity: Any = None
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    hooks_executed: List[str] = field(default_factory=list)
    hooks_failed: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class StateMachine:
    """
    状态机基类
    
    提供完整的状态管理功能：
    - 状态定义和验证
    - 转换规则管理
    - 转换钩子（before/after/around）
    - 状态历史记录
    
    使用示例：
        class UserStateMachine(StateMachine):
            STATES = [
                State("active", is_initial=True),
                State("locked"),
                State("inactive")
            ]
            TRANSITIONS = {
                "active": ["locked", "inactive"],
                "locked": ["active", "inactive"],
                "inactive": ["active"]
            }
    """

    # 子类重写：状态定义列表
    STATES: List[State] = []

    # 子类重写：转换规则 {当前状态: [可转换目标状态列表]}
    TRANSITIONS: Dict[str, List[str]] = {}

    # 子类重写：状态字段名（实体中存储状态的字段）
    STATE_FIELD: str = "status"

    def __init__(self, entity: Any):
        """
        初始化状态机
        
        @param entity: 关联的实体实例
        """
        self.entity = entity
        self._hooks: Dict[str, List[Callable]] = {
            "before": [],
            "after": [],
            "around": []
        }
        self._state_history: List[Dict] = []

        # 初始化状态
        self._init_state()

    def _init_state(self):
        """初始化实体状态"""
        current_state = self.current_state

        if current_state is None:
            # 设置为初始状态
            initial_state = self.get_initial_state()
            if initial_state:
                self._set_state(initial_state.name)

    @property
    def current_state(self) -> Optional[str]:
        """获取当前状态"""
        return getattr(self.entity, self.STATE_FIELD, None)

    def _set_state(self, state_name: str):
        """设置状态（内部方法）"""
        setattr(self.entity, self.STATE_FIELD, state_name)

    @classmethod
    def get_states(cls) -> List[State]:
        """获取所有状态定义"""
        return cls.STATES

    @classmethod
    def get_state_names(cls) -> List[str]:
        """获取所有状态名称"""
        return [s.name for s in cls.STATES]

    @classmethod
    def get_initial_state(cls) -> Optional[State]:
        """获取初始状态"""
        for state in cls.STATES:
            if state.is_initial:
                return state
        # 如果没有标记初始状态，返回第一个
        return cls.STATES[0] if cls.STATES else None

    @classmethod
    def is_valid_state(cls, state_name: str) -> bool:
        """检查状态是否有效"""
        return state_name in cls.get_state_names()

    @classmethod
    def get_allowed_transitions(cls, from_state: str) -> List[str]:
        """获取从指定状态可转换的目标状态列表"""
        return cls.TRANSITIONS.get(from_state, [])

    @classmethod
    def can_transition(cls, from_state: str, to_state: str) -> bool:
        """检查是否可以从from_state转换到to_state"""
        if not cls.is_valid_state(from_state) or not cls.is_valid_state(to_state):
            return False
        return to_state in cls.get_allowed_transitions(from_state)

    def can_transition_to(self, to_state: str, **context) -> bool:
        """检查当前状态是否可以转换到目标状态"""
        from_state = self.current_state

        # 检查状态有效性
        if not self.is_valid_state(to_state):
            return False

        # 检查转换规则
        if not self.can_transition(from_state, to_state):
            return False

        # 检查转换条件（如果有）
        transition = self._get_transition(from_state, to_state)
        if transition and transition.condition:
            return transition.can_execute(self.entity, **context)

        return True

    def _get_transition(self, from_state: str, to_state: str) -> Optional[Transition]:
        """获取转换定义"""
        # 简化实现，实际项目中可能需要更复杂的查找逻辑
        if self.can_transition(from_state, to_state):
            return Transition(from_state=from_state, to_state=to_state)
        return None

    def transition_to(
            self,
            to_state: str,
            validate: bool = True,
            execute_hooks: bool = True,
            record_history: bool = True,
            **context
    ) -> TransitionResult:
        """
        转换到目标状态
        
        @param to_state: 目标状态
        @param validate: 是否验证转换
        @param execute_hooks: 是否执行钩子
        @param record_history: 是否记录历史
        @param context: 上下文参数
        @return: 转换结果
        """
        from_state = self.current_state

        # 验证转换
        if validate:
            if not self.is_valid_state(to_state):
                return TransitionResult(
                    success=False,
                    from_state=from_state,
                    to_state=to_state,
                    message=f"无效的目标状态: {to_state}"
                )

            if not self.can_transition_to(to_state, **context):
                allowed = self.get_allowed_transitions(from_state)
                return TransitionResult(
                    success=False,
                    from_state=from_state,
                    to_state=to_state,
                    message=f"不允许的状态转换: {from_state} -> {to_state}，允许: {allowed}"
                )

        hooks_executed = []
        hooks_failed = []

        try:
            # 执行 before 钩子
            if execute_hooks:
                self._execute_hooks("before", from_state, to_state, hooks_executed, hooks_failed)

            # 执行 around 钩子（前半部分）
            if execute_hooks:
                self._execute_hooks("around", from_state, to_state, hooks_executed, hooks_failed, phase="before")

            # 执行状态转换
            self._set_state(to_state)

            # 执行 around 钩子（后半部分）
            if execute_hooks:
                self._execute_hooks("around", from_state, to_state, hooks_executed, hooks_failed, phase="after")

            # 执行 after 钩子
            if execute_hooks:
                self._execute_hooks("after", from_state, to_state, hooks_executed, hooks_failed)

            # 记录历史
            if record_history:
                self._record_transition(from_state, to_state)

            return TransitionResult(
                success=True,
                from_state=from_state,
                to_state=to_state,
                entity=self.entity,
                hooks_executed=hooks_executed,
                hooks_failed=hooks_failed,
                message=f"状态转换成功: {from_state} -> {to_state}"
            )

        except TransitionHookError as e:
            # 钩子执行失败，回滚状态
            self._set_state(from_state)
            return TransitionResult(
                success=False,
                from_state=from_state,
                to_state=to_state,
                hooks_executed=hooks_executed,
                hooks_failed=hooks_failed + [e.hook_name],
                message=f"状态转换失败（钩子错误）: {e}"
            )

    def _execute_hooks(
            self,
            hook_type: str,
            from_state: str,
            to_state: str,
            executed: List[str],
            failed: List[str],
            phase: Optional[str] = None
    ):
        """执行钩子"""
        hooks = self._hooks.get(hook_type, [])

        for hook in hooks:
            hook_name = hook.__name__ if hasattr(hook, "__name__") else str(hook)

            try:
                if hook_type == "around":
                    hook(self.entity, from_state, to_state, phase)
                else:
                    hook(self.entity, from_state, to_state)
                executed.append(hook_name)
            except Exception as e:
                failed.append(hook_name)
                raise TransitionHookError(hook_name, from_state, to_state, e)

    def _record_transition(self, from_state: str, to_state: str):
        """记录状态转换历史"""
        self._state_history.append({
            "from": from_state,
            "to": to_state,
            "timestamp": datetime.now().isoformat()
        })

    def add_hook(self, hook_type: str, hook: Callable):
        """
        添加状态转换钩子
        
        @param hook_type: 钩子类型（before/after/around）
        @param hook: 钩子函数
        """
        if hook_type not in self._hooks:
            raise ValueError(f"无效的钩子类型: {hook_type}")
        self._hooks[hook_type].append(hook)

    def remove_hook(self, hook_type: str, hook: Callable):
        """移除状态转换钩子"""
        if hook_type in self._hooks and hook in self._hooks[hook_type]:
            self._hooks[hook_type].remove(hook)

    def get_state_history(self) -> List[Dict]:
        """获取状态转换历史"""
        return self._state_history.copy()

    def is_in_state(self, state_name: str) -> bool:
        """检查当前是否处于指定状态"""
        return self.current_state == state_name

    def __repr__(self):
        return f"StateMachine({self.current_state})"
