# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: AllureAdapter - 核心适配器
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
AllureAdapter - Allure 报告核心适配器

提供与 Allure 框架的基础集成能力，包括：
- 步骤记录
- 附件生成
- 标签管理
- 测试元数据设置

使用示例：
    from pe.reporting.adapter import AllureAdapter
    
    # 记录步骤
    with AllureAdapter.step("创建用户"):
        user = create_user()
    
    # 附加数据
    AllureAdapter.attach_json("用户信息", user.to_dict())
"""

import json
from typing import Any, Dict, Optional, Callable
from functools import wraps

try:
    import allure
    from allure_commons.types import AttachmentType
    HAS_ALLURE = True
except ImportError:
    HAS_ALLURE = False
    AttachmentType = None


class NullContext:
    """空上下文管理器（当 Allure 不可用时使用）"""
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class AllureAdapter:
    """Allure 适配器 - 核心功能封装"""

    @staticmethod
    def is_available() -> bool:
        """检查 Allure 是否可用"""
        return HAS_ALLURE

    # ========== 标签管理 ==========
    
    @staticmethod
    def feature(name: str):
        """标记功能模块"""
        if HAS_ALLURE:
            allure.feature(name)

    @staticmethod
    def story(name: str):
        """标记用户故事"""
        if HAS_ALLURE:
            allure.story(name)

    @staticmethod
    def title(name: str):
        """设置测试标题"""
        if HAS_ALLURE:
            allure.title(name)

    @staticmethod
    def description(text: str):
        """设置测试描述"""
        if HAS_ALLURE:
            allure.description(text)

    @staticmethod
    def severity(level: str):
        """设置严重级别
        
        Args:
            level: blocker, critical, normal, minor, trivial
        """
        if HAS_ALLURE:
            allure.severity(getattr(allure.severity_level, level.upper(), allure.severity_level.NORMAL))

    @staticmethod
    def tag(*tags: str):
        """添加标签"""
        if HAS_ALLURE:
            for tag in tags:
                allure.tag(tag)

    @staticmethod
    def label(name: str, value: str):
        """添加自定义标签"""
        if HAS_ALLURE:
            allure.label(name, value)

    # ========== 步骤管理 ==========
    
    @staticmethod
    def step(name: str):
        """记录测试步骤
        
        使用示例：
            with AllureAdapter.step("创建用户"):
                user = UserEntity(username="test")
        """
        if HAS_ALLURE:
            return allure.step(name)
        return NullContext()

    @staticmethod
    def nested_step(name: str):
        """创建嵌套步骤（用于动态步骤）"""
        if HAS_ALLURE:
            return allure.step(name)
        return NullContext()

    # ========== 附件管理 ==========
    
    @staticmethod
    def attach_json(name: str, data: Dict[str, Any]):
        """附加 JSON 数据"""
        if HAS_ALLURE:
            allure.attach(
                json.dumps(data, ensure_ascii=False, indent=2, default=str),
                name=name,
                attachment_type=AttachmentType.JSON
            )

    @staticmethod
    def attach_text(name: str, text: str):
        """附加文本数据"""
        if HAS_ALLURE:
            allure.attach(text, name=name, attachment_type=AttachmentType.TEXT)

    @staticmethod
    def attach_html(name: str, html: str):
        """附加 HTML 数据"""
        if HAS_ALLURE:
            allure.attach(html, name=name, attachment_type=AttachmentType.HTML)

    @staticmethod
    def attach_image(name: str, image_bytes: bytes):
        """附加图片数据"""
        if HAS_ALLURE:
            allure.attach(image_bytes, name=name, attachment_type=AttachmentType.PNG)

    @staticmethod
    def attach_file(filepath: str, name: Optional[str] = None):
        """附加文件"""
        if HAS_ALLURE:
            allure.attach.file(filepath, name=name or filepath)

    @staticmethod
    def attach_bytes(name: str, data: bytes, mime_type: str = "application/octet-stream"):
        """附加二进制数据"""
        if HAS_ALLURE:
            allure.attach(data, name=name, attachment_type=mime_type)

    # ========== 装饰器 ==========
    
    @staticmethod
    def step_decorator(name: str):
        """步骤装饰器
        
        使用示例：
            @AllureAdapter.step_decorator("创建用户")
            def create_user():
                return UserEntity()
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                step_name = name.format(*args, **kwargs)
                with AllureAdapter.step(step_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


# 便捷函数
step = AllureAdapter.step
attach_json = AllureAdapter.attach_json
attach_text = AllureAdapter.attach_text
attach_html = AllureAdapter.attach_html
attach_image = AllureAdapter.attach_image
attach_file = AllureAdapter.attach_file

feature = AllureAdapter.feature
story = AllureAdapter.story
title = AllureAdapter.title
description = AllureAdapter.description
severity = AllureAdapter.severity
tag = AllureAdapter.tag
label = AllureAdapter.label
