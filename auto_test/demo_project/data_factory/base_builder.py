# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 基础数据构建器
# @Time   : 2026-03-31
# @Author : 毛鹏
import random
import string
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any


class BaseDataBuilder(ABC):
    """基础数据构建器 - 提供通用的数据生成方法"""

    def generate_random_string(self, length: int = 10) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_random_number(self, min_val: int = 1, max_val: int = 1000) -> int:
        """生成随机数字"""
        return random.randint(min_val, max_val)

    def generate_random_email(self) -> str:
        """生成随机邮箱"""
        return f"test_{self.generate_random_string(8)}@example.com"

    def generate_random_phone(self) -> str:
        """生成随机手机号"""
        return f"1{random.randint(3, 9)}{''.join(random.choices(string.digits, k=9))}"

    def generate_timestamp(self, days_offset: int = 0) -> str:
        """生成时间戳"""
        target_date = datetime.now() + timedelta(days=days_offset)
        return target_date.strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def build_default_data(self) -> Dict[str, Any]:
        """构建默认数据 - 子类必须实现"""
        pass

    @abstractmethod
    def build_custom_data(self, **kwargs) -> Dict[str, Any]:
        """构建自定义数据 - 子类必须实现"""
        pass


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
