# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 项目特定数据构建器
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Any

from core.base import BaseDataBuilder


class ApprovalFlowBuilder(BaseDataBuilder):
    """审批流数据构建器"""

    def build_default_data(self) -> Dict[str, Any]:
        """构建默认审批流数据"""
        return {
            "flow_name": f"审批流_{self.generate_random_string(6)}",
            "flow_code": f"FLOW_{self.generate_random_string(8).upper()}",
            "description": f"测试审批流描述_{self.generate_random_string(10)}",
            "status": "active",
            "created_time": self.generate_timestamp(),
            "creator": f"user_{self.generate_random_string(6)}"
        }

    def build_custom_data(self, **kwargs) -> Dict[str, Any]:
        """构建自定义审批流数据"""
        default_data = self.build_default_data()
        # 使用传入的参数覆盖默认值
        default_data.update(kwargs)
        return default_data


class UserDataBuilder(BaseDataBuilder):
    """用户数据构建器"""

    def build_default_data(self) -> Dict[str, Any]:
        """构建默认用户数据"""
        return {
            "username": f"test_user_{self.generate_random_string(6)}",
            "email": self.generate_random_email(),
            "phone": self.generate_random_phone(),
            "department": f"部门_{self.generate_random_string(4)}",
            "role": "user",
            "status": "active",
            "created_time": self.generate_timestamp()
        }

    def build_custom_data(self, **kwargs) -> Dict[str, Any]:
        """构建自定义用户数据"""
        default_data = self.build_default_data()
        default_data.update(kwargs)
        return default_data
