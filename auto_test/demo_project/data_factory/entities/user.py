# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户实体 - 集成状态机
# @Time   : 2026-04-01
# @Author : 毛鹏
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from .base_entity import BaseEntity

if TYPE_CHECKING:
    from ..state_machine import UserStateMachine, TransitionResult


@dataclass
class UserEntity(BaseEntity):
    """
    用户实体 - 集成状态机
    
    对应 mock_api 中的 User 模型
    
    状态流转：
        active <-> locked <-> inactive
        
    使用示例：
        # 创建用户（初始状态为 active）
        user = UserEntity(username="test", password="123456")
        print(user.status)  # "active"
        
        # 状态转换
        user.lock()      # active -> locked
        user.unlock()    # locked -> active
        user.deactivate()  # active -> inactive
        user.activate()   # inactive -> active
        
        # 检查状态
        if user.is_active():
            print("用户可以登录")
    """
    
    # 用户基本信息
    username: str = ""
    email: str = ""
    full_name: str = ""
    password: str = ""
    
    # 角色信息
    role: str = "user"  # user, admin, dept_manager, finance_manager, ceo
    
    # 状态（集成状态机）
    status: str = "active"  # active, locked, inactive
    
    # 登录失败次数（用于自动锁定）
    login_failures: int = 0
    
    def __post_init__(self):
        """初始化后设置默认状态"""
        super().__post_init__()
        # 如果没有设置状态，使用初始状态
        if not self.status:
            self.status = "active"
    
    @property
    def _state_machine(self) -> "UserStateMachine":
        """获取状态机实例（延迟加载）"""
        from ..state_machine import UserStateMachine
        if not hasattr(self, "__state_machine"):
            self.__state_machine = UserStateMachine(self)
        return self.__state_machine
    
    # ==================== 状态检查方法 ====================
    
    def is_active(self) -> bool:
        """检查是否处于正常状态"""
        return self.status == "active"
    
    def is_locked(self) -> bool:
        """检查是否处于锁定状态"""
        return self.status == "locked"
    
    def is_inactive(self) -> bool:
        """检查是否处于注销状态"""
        return self.status == "inactive"
    
    # ==================== 状态转换方法 ====================
    
    def lock(self) -> "TransitionResult":
        """
        锁定用户（active -> locked）
        
        @return: 转换结果
        """
        return self._state_machine.transition_to("locked")
    
    def unlock(self) -> "TransitionResult":
        """
        解锁用户（locked -> active）
        
        @return: 转换结果
        """
        result = self._state_machine.transition_to("active")
        if result.success:
            self.login_failures = 0  # 重置登录失败次数
        return result
    
    def deactivate(self) -> "TransitionResult":
        """
        注销用户（active/locked -> inactive）
        
        @return: 转换结果
        """
        return self._state_machine.transition_to("inactive")
    
    def activate(self) -> "TransitionResult":
        """
        重新激活用户（inactive -> active）
        
        @return: 转换结果
        """
        return self._state_machine.transition_to("active")
    
    def transition_to(self, target_state: str, **context) -> "TransitionResult":
        """
        转换到指定状态
        
        @param target_state: 目标状态
        @param context: 上下文参数
        @return: 转换结果
        """
        return self._state_machine.transition_to(target_state, **context)
    
    def can_transition_to(self, target_state: str, **context) -> bool:
        """
        检查是否可以转换到目标状态
        
        @param target_state: 目标状态
        @param context: 上下文参数
        @return: 是否可以转换
        """
        return self._state_machine.can_transition_to(target_state, **context)
    
    # ==================== 业务行为方法 ====================
    
    def record_login_failure(self) -> bool:
        """
        记录登录失败
        
        当登录失败3次时自动锁定账户
        
        @return: 是否触发了锁定
        """
        if self.is_active():
            self.login_failures += 1
            if self.login_failures >= 3:
                self.lock()
                return True
        return False
    
    def record_login_success(self):
        """记录登录成功，重置失败次数"""
        if self.login_failures > 0:
            self.login_failures = 0
    
    # ==================== 智能工厂方法 ====================
    
    @classmethod
    def active(cls, **kwargs) -> "UserEntity":
        """
        创建正常状态的用户
        
        @param kwargs: 用户属性
        @return: UserEntity实例（状态为 active）
        """
        return cls(status="active", **kwargs)
    
    @classmethod
    def locked(cls, **kwargs) -> "UserEntity":
        """
        创建锁定状态的用户
        
        @param kwargs: 用户属性
        @return: UserEntity实例（状态为 locked）
        """
        return cls(status="locked", login_failures=3, **kwargs)
    
    @classmethod
    def inactive(cls, **kwargs) -> "UserEntity":
        """
        创建注销状态的用户
        
        @param kwargs: 用户属性
        @return: UserEntity实例（状态为 inactive）
        """
        return cls(status="inactive", **kwargs)
    
    # ==================== 基础方法 ====================
    
    def validate(self) -> bool:
        """
        验证用户数据有效性
        
        @return: 是否有效
        """
        if not self.username or len(self.username) < 3:
            return False
        
        if not self.email or "@" not in self.email:
            return False
        
        if not self.password or len(self.password) < 6:
            return False
        
        # 验证状态有效性
        valid_states = ["active", "locked", "inactive"]
        if self.status not in valid_states:
            return False
        
        return True
    
    def get_dependencies(self) -> List[str]:
        """获取依赖的实体类型"""
        return []  # 用户是基础实体，无依赖
    
    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为API请求体
        
        @return: API请求体字典
        """
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "password": self.password,
            "status": self.status
        }
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "UserEntity":
        """
        从API响应创建实体
        
        @param data: API响应数据
        @return: UserEntity实例
        """
        entity = cls(
            id=data.get("id"),
            username=data.get("username", ""),
            email=data.get("email", ""),
            full_name=data.get("full_name", ""),
            password=data.get("password", ""),
            role=data.get("role", "user"),
            status=data.get("status", "active"),
            login_failures=data.get("login_failures", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        entity._is_new = False
        return entity
