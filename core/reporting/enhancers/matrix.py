# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 变体矩阵展示增强器
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
变体矩阵展示增强器

将变体矩阵信息可视化到 Allure 报告，包括：
- 变体矩阵参数
- 维度信息
- 组合统计

使用示例：
    from pe.reporting.enhancers import MatrixEnhancer
    
    # 附加变体信息
    MatrixEnhancer.attach_variant_info("admin_correct", {"role": "admin", "valid": True})
    
    # 附加变体矩阵
    MatrixEnhancer.attach_variant_matrix(variant_matrix)
"""

from typing import Any, Dict, Optional

from ..adapter import AllureAdapter


class MatrixEnhancer:
    """变体矩阵展示增强器"""

    @staticmethod
    def attach_variant_info(variant_name: str, variant_data: Dict[str, Any]):
        """附加变体信息
        
        Args:
            variant_name: 变体名称
            variant_data: 变体数据
        """
        AllureAdapter.title(f"变体: {variant_name}")
        
        with AllureAdapter.step(f"变体参数: {variant_name}"):
            AllureAdapter.attach_json("变体参数", variant_data)

    @staticmethod
    def attach_variant_matrix(matrix):
        """附加变体矩阵
        
        Args:
            matrix: 变体矩阵对象
        """
        if not hasattr(matrix, 'dimensions'):
            return

        # 构建矩阵数据
        matrix_data = {
            "dimensions": [
                {
                    "name": dim.name,
                    "variants": [
                        {
                            "name": v.name,
                            "data": v.data,
                            "order": v.order
                        }
                        for v in dim.variants
                    ]
                }
                for dim in matrix.dimensions
            ],
            "total_combinations": len(matrix.generate()) if hasattr(matrix, 'generate') else 0
        }

        with AllureAdapter.step("变体矩阵"):
            AllureAdapter.attach_json("变体矩阵数据", matrix_data)

    @staticmethod
    def attach_variant_summary(matrix):
        """附加变体摘要（简化版）
        
        Args:
            matrix: 变体矩阵对象
        """
        if not hasattr(matrix, 'dimensions'):
            return

        summary = {
            "维度数": len(matrix.dimensions),
            "总组合数": len(matrix.generate()) if hasattr(matrix, 'generate') else 0,
            "维度详情": [
                {
                    "名称": dim.name,
                    "变体数": len(dim.variants)
                }
                for dim in matrix.dimensions
            ]
        }

        AllureAdapter.attach_json("变体摘要", summary)
