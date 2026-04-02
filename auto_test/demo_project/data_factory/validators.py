# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据校验器
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Any, Dict, List, Optional, Callable


class ValidationError(Exception):
    """数据校验错误"""
    pass


class ValidationRule:
    """校验规则"""

    def __init__(self, field: str, validator: Callable, message: str = None):
        self.field = field
        self.validator = validator
        self.message = message or f"字段 '{field}' 校验失败"

    def validate(self, data: Dict) -> bool:
        """执行校验"""
        value = data.get(self.field)
        if not self.validator(value):
            raise ValidationError(self.message)
        return True


class DataValidator:
    """
    数据校验器
    用于校验数据是否符合要求
    """

    def __init__(self):
        self.rules: List[ValidationRule] = []

    def add_rule(self, field: str, validator: Callable, message: str = None):
        """添加校验规则"""
        self.rules.append(ValidationRule(field, validator, message))
        return self

    def validate(self, data: Dict) -> bool:
        """
        校验数据
        @param data: 待校验的数据
        @return: 是否校验通过
        @raises ValidationError: 校验失败时抛出
        """
        for rule in self.rules:
            rule.validate(data)
        return True

    def validate_required(self, *fields: str):
        """添加必填字段校验"""
        for field in fields:
            self.add_rule(
                field,
                lambda x: x is not None and x != "",
                f"字段 '{field}' 为必填项"
            )
        return self

    def validate_type(self, field: str, expected_type: type):
        """添加类型校验"""
        self.add_rule(
            field,
            lambda x: isinstance(x, expected_type) if x is not None else True,
            f"字段 '{field}' 类型必须为 {expected_type.__name__}"
        )
        return self

    def validate_range(self, field: str, min_val: Optional[float] = None, max_val: Optional[float] = None):
        """添加范围校验"""

        def validator(value):
            if value is None:
                return True
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True

        message = f"字段 '{field}'"
        if min_val is not None:
            message += f" 最小值为 {min_val}"
        if max_val is not None:
            message += f"{' 且' if min_val is not None else ''} 最大值为 {max_val}"

        self.add_rule(field, validator, message)
        return self

    def validate_length(self, field: str, min_len: Optional[int] = None, max_len: Optional[int] = None):
        """添加长度校验"""

        def validator(value):
            if value is None:
                return True
            length = len(str(value))
            if min_len is not None and length < min_len:
                return False
            if max_len is not None and length > max_len:
                return False
            return True

        message = f"字段 '{field}' 长度"
        if min_len is not None:
            message += f" 至少 {min_len}"
        if max_len is not None:
            message += f"{' 且' if min_len is not None else ''} 最多 {max_len}"

        self.add_rule(field, validator, message)
        return self

    def validate_pattern(self, field: str, pattern: str, message: str = None):
        """添加正则表达式校验"""
        import re
        compiled_pattern = re.compile(pattern)
        self.add_rule(
            field,
            lambda x: bool(compiled_pattern.match(str(x))) if x is not None else True,
            message or f"字段 '{field}' 格式不符合要求"
        )
        return self

    def clear(self):
        """清空所有规则"""
        self.rules.clear()


# 常用校验器
class CommonValidators:
    """常用校验方法集合"""

    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """非空校验"""
        return value is not None and value != ""

    @staticmethod
    def is_positive_number(value: Any) -> bool:
        """正数校验"""
        try:
            return float(value) > 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def is_email(value: str) -> bool:
        """邮箱格式校验"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(value))) if value else False

    @staticmethod
    def is_phone(value: str) -> bool:
        """手机号格式校验"""
        import re
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, str(value))) if value else False
