# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core 认证管理 - 统一认证处理
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core 认证管理模块

提供统一的认证管理功能
"""

from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta


class AuthManager:
    """
    认证管理器
    
    管理认证 token 的获取、刷新和失效
    
    使用示例：
        auth = AuthManager()
        auth.set_token("your_token", expires_in=3600)
        
        if auth.is_valid():
            token = auth.get_token()
        else:
            auth.refresh_token()
    """
    
    def __init__(self):
        self._token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
        self._token_type: str = "Bearer"
        self._refresh_callback: Optional[Callable] = None
    
    def set_token(
        self,
        token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        token_type: str = "Bearer"
    ):
        """
        设置 token
        
        @param token: 访问 token
        @param refresh_token: 刷新 token
        @param expires_in: 过期时间（秒）
        @param token_type: token 类型
        """
        self._token = token
        self._refresh_token = refresh_token
        self._token_type = token_type
        
        if expires_in:
            self._expires_at = datetime.now() + timedelta(seconds=expires_in)
        else:
            self._expires_at = None
    
    def get_token(self) -> Optional[str]:
        """获取当前 token"""
        return self._token
    
    def get_auth_header(self) -> Optional[str]:
        """获取认证头值"""
        if self._token:
            return f"{self._token_type} {self._token}"
        return None
    
    def is_valid(self) -> bool:
        """检查 token 是否有效"""
        if not self._token:
            return False
        
        if self._expires_at and datetime.now() >= self._expires_at:
            return False
        
        return True
    
    def is_expired(self) -> bool:
        """检查 token 是否已过期"""
        if not self._expires_at:
            return False
        return datetime.now() >= self._expires_at
    
    def set_refresh_callback(self, callback: Callable[[], str]):
        """
        设置刷新回调函数
        
        @param callback: 刷新回调函数，返回新的 token
        """
        self._refresh_callback = callback
    
    def refresh_token(self) -> Optional[str]:
        """
        刷新 token
        
        @return: 新的 token
        """
        if self._refresh_callback:
            new_token = self._refresh_callback()
            if new_token:
                self._token = new_token
                return new_token
        
        return None
    
    def clear(self):
        """清除认证信息"""
        self._token = None
        self._refresh_token = None
        self._expires_at = None
    
    def get_info(self) -> Dict[str, Any]:
        """获取认证信息"""
        return {
            "has_token": self._token is not None,
            "has_refresh_token": self._refresh_token is not None,
            "is_valid": self.is_valid(),
            "is_expired": self.is_expired(),
            "expires_at": self._expires_at.isoformat() if self._expires_at else None,
            "token_type": self._token_type,
        }


class TokenStorage:
    """
    Token 存储基类
    
    定义 token 存储接口
    """
    
    def save(self, key: str, token: str) -> bool:
        """保存 token"""
        raise NotImplementedError
    
    def load(self, key: str) -> Optional[str]:
        """加载 token"""
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        """删除 token"""
        raise NotImplementedError


class MemoryTokenStorage(TokenStorage):
    """内存 Token 存储"""
    
    def __init__(self):
        self._storage: Dict[str, str] = {}
    
    def save(self, key: str, token: str) -> bool:
        self._storage[key] = token
        return True
    
    def load(self, key: str) -> Optional[str]:
        return self._storage.get(key)
    
    def delete(self, key: str) -> bool:
        if key in self._storage:
            del self._storage[key]
            return True
        return False


__all__ = [
    "AuthManager",
    "TokenStorage",
    "MemoryTokenStorage",
]
