# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘节点定义
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
数据血缘节点模块

定义血缘追踪中的核心数据结构：
- LineageNodeType: 节点类型枚举
- LineageRelation: 关系类型枚举  
- DataLineageNode: 血缘节点（实体）
- LineageEdge: 血缘边（关系）

注意：枚举和模型已从 enums.demo_enum 和 models.demo_model 导入
"""

# 从统一的枚举和模型文件导入
from core.enums.demo_enum import LineageNodeType, LineageRelation
from models.demo_model import LineageEdge, DataLineageNode, LineagePath

# 保持向后兼容的导出
__all__ = [
    'LineageNodeType', 'LineageRelation',
    'LineageEdge', 'DataLineageNode', 'LineagePath'
]
