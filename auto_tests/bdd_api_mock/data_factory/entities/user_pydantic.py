# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户实体 - Pydantic 版本 (L3 实体层)
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
用户实体 - L3 实体层

使用 Pydantic 定义数据模型，提供 to_api_payload() 方法

状态流转：
    active <-> locked <-> inactive
"""

from typing import Any, Dict, Optional

from pydantic import Field

from core.base import PydanticEntity


class UserEntity(PydanticEntity):
    """
    用户实体 - L3 实体层
    
    对应 mock_api 中的 User 模型
    
    Attributes:
        id: 用户ID（响应字段，创建后填充）
        username: 用户名（请求字段）
        email: 邮箱（请求字段）
        full_name: 全名（请求字段）
        password: 密码（请求字段，创建时必填）
        role: 角色（请求字段）
        status: 状态（响应字段）
    """
    
    # 请求字段（创建时需要）
    username: str = Field(default="", min_length=1, description="用户名")
    email: str = Field(default="", description="邮箱")
    full_name: str = Field(default="", description="全名")
    password: str = Field(default="", min_length=1, description="密码")
    role: str = Field(default="user", description="角色")
    
    # 响应字段（创建后填充）
    login_failures: int = Field(default=0, description="登录失败次数")
    
    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为 API 请求体 - 注册/创建用户
        
        @return: API 请求体字典
        """
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "password": self.password,
        }
    
    def to_login_payload(self) -> Dict[str, Any]:
        """
        转换为登录请求体
        
        @return: 登录请求体字典
        """
        return {
            "username": self.username,
            "password": self.password,
        }
    
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
    
    # ==================== 工厂方法 ====================
    
    @classmethod
    def default(cls) -> "UserEntity":
        """创建默认用户"""
        import uuid
        return cls(
            username=f"user_{uuid.uuid4().hex[:8]}",
            email=f"{uuid.uuid4().hex[:8]}@example.com",
            full_name="Test User",
            password="password123",
            role="user",
        )
    
    @classmethod
    def admin(cls) -> "UserEntity":
        """创建管理员用户"""
        import uuid
        return cls(
            username=f"admin_{uuid.uuid4().hex[:8]}",
            email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
            full_name="Admin User",
            password="admin123",
            role="admin",
        )
    
    @classmethod
    def with_credentials(cls, username: str, password: str) -> "UserEntity":
        """使用指定凭据创建用户"""
        return cls(
            username=username,
            password=password,
            email=f"{username}@example.com",
            full_name=username,
        )
