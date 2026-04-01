# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户实体
# @Time   : 2026-03-31
# @Author : 毛鹏
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from .base_entity import BaseEntity


@dataclass
class UserEntity(BaseEntity):
    """
    用户实体
    
    对应 mock_api 中的 User 模型
    """
    
    # 用户基本信息
    username: str = ""
    email: str = ""
    full_name: str = ""
    password: str = ""
    
    # 角色信息
    role: str = "user"  # user, admin, dept_manager, finance_manager, ceo
    
    # 状态
    is_active: bool = True
    
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
            "password": self.password
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
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            status=data.get("status", "active")
        )
        entity._is_new = False
        return entity
