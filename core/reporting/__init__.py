# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报告模块 - 支持多种测试报告格式
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
PE 报告模块

提供统一的测试报告功能，目前支持：
- Allure 报告深度集成

目录结构：
    pe/reporting/
    ├── adapter.py          # AllureAdapter (核心适配)
    ├── hooks.py            # pytest 钩子集成
    ├── enhancers/          # 增强器 (PE 特色功能)
    │   ├── lineage.py      # 血缘图可视化
    │   ├── matrix.py       # 变体矩阵展示
    │   └── state_machine.py # 状态流转图
    ├── attachments/        # 附件生成器
    ├── labels/             # 标签体系
    └── steps/              # 步骤封装

使用示例：
    # 基础使用
    from pe.reporting import AllureAdapter, step
    
    with step("执行测试步骤"):
        # 测试代码
        pass
    
    # 使用装饰器
    from pe.reporting import allure_feature, allure_story
    
    @allure_feature("用户管理")
    @allure_story("用户创建")
    def test_create_user():
        pass
    
    # 使用增强器
    from pe.reporting.enhancers import LineageEnhancer
    LineageEnhancer.attach_lineage_graph(tracker)
"""

# 核心适配器
from .adapter import (
    AllureAdapter,
    step,
    attach_json,
    attach_text,
    attach_html,
    attach_image,
    attach_file,
    feature,
    story,
    title,
    description,
    severity,
    tag,
    label,
)
# 增强器
from .enhancers import (
    LineageEnhancer,
    MatrixEnhancer,
    StateMachineEnhancer,
)
# fixtures
from .fixtures import (
    allure_context,
    allure_lineage,
    allure_variant,
)
# pytest 钩子和装饰器
from .hooks import (
    pytest_configure,
    allure_feature,
    allure_story,
    allure_severity,
    allure_tag,
    allure_label,
)

__all__ = [
    # 核心适配器
    "AllureAdapter",
    # 便捷函数
    "step",
    "attach_json",
    "attach_text",
    "attach_html",
    "attach_image",
    "attach_file",
    # 标签
    "feature",
    "story",
    "title",
    "description",
    "severity",
    "tag",
    "label",
    # fixtures
    "allure_context",
    "allure_lineage",
    "allure_variant",
    # pytest 钩子
    "pytest_configure",
    # 装饰器
    "allure_feature",
    "allure_story",
    "allure_severity",
    "allure_tag",
    "allure_label",
    # 增强器
    "LineageEnhancer",
    "MatrixEnhancer",
    "StateMachineEnhancer",
]
