# -*- coding: utf-8 -*-
"""
实体上下文管理器

管理 BDD 场景中的实体，支持：
- 命名实体存储
- 按别名查找
- 属性访问
- 多实体管理
"""

from typing import Any, Dict, Optional


class EntityContext:
    """实体上下文管理器
    
    每个 BDD 场景拥有独立的上下文实例，通过 fixture 注入。
    支持存储多个命名实体，并在步骤间传递。
    
    示例:
        >>> context = EntityContext()
        >>> context.add("产品A", product_entity)
        >>> context.get("产品A")  # 返回 product_entity
        >>> context.get_attr("产品A", "id")  # 返回 product_entity.id
    """
    
    def __init__(self):
        self._entities: Dict[str, Any] = {}
    
    def add(self, alias: str, entity: Any) -> None:
        """添加命名实体到上下文
        
        @param alias: 实体别名，用于后续引用
        @param entity: 实体对象
        """
        self._entities[alias] = entity
    
    def get(self, alias: str) -> Any:
        """获取命名实体
        
        @param alias: 实体别名
        @return: 实体对象
        @raises KeyError: 如果别名不存在
        """
        if alias not in self._entities:
            available = ", ".join(self._entities.keys()) if self._entities else "无"
            raise KeyError(
                f"实体别名 '{alias}' 未找到。\n"
                f"请确保先执行 '假如 存在\"xxx\" 作为 @{alias}' 步骤。\n"
                f"可用别名: {available}"
            )
        return self._entities[alias]
    
    def get_attr(self, alias: str, attr: str) -> Any:
        """获取实体的属性值
        
        @param alias: 实体别名
        @param attr: 属性名
        @return: 属性值
        @raises KeyError: 如果别名不存在
        @raises AttributeError: 如果属性不存在
        """
        entity = self.get(alias)
        if not hasattr(entity, attr):
            available = [a for a in dir(entity) if not a.startswith('_')]
            raise AttributeError(
                f"实体 '{alias}' 没有属性 '{attr}'。\n"
                f"可用属性: {', '.join(available[:10])}..."
            )
        return getattr(entity, attr)
    
    def has(self, alias: str) -> bool:
        """检查别名是否存在
        
        @param alias: 实体别名
        @return: 是否存在
        """
        return alias in self._entities
    
    def remove(self, alias: str) -> None:
        """移除命名实体
        
        @param alias: 实体别名
        """
        if alias in self._entities:
            del self._entities[alias]
    
    def clear(self) -> None:
        """清空所有实体"""
        self._entities.clear()
    
    def list_aliases(self) -> list:
        """列出所有可用的别名
        
        @return: 别名列表
        """
        return list(self._entities.keys())
    
    def build_placeholder_context(self, docstring: str) -> Dict[str, Any]:
        """从 docstring 中提取占位符并构建替换上下文
        
        支持格式: ${{alias.attr}} 或 @alias.attr
        
        @param docstring: 包含占位符的字符串
        @return: 占位符到值的映射字典
        """
        import re
        context = {}
        
        # 匹配 ${{alias.attr}} 格式
        pattern1 = r'\$\{\{(\w+)\.(\w+)\}\}'
        matches1 = re.findall(pattern1, docstring)
        
        # 匹配 @alias.attr 格式
        pattern2 = r'@(\w+)\.(\w+)'
        matches2 = re.findall(pattern2, docstring)
        
        for alias, attr in matches1 + matches2:
            key = f"{alias}.{attr}"
            value = self.get_attr(alias, attr)
            context[key] = value
            # 同时存储两种格式的 key
            context[f"${{{{{alias}.{attr}}}}}"] = value
            context[f"@{alias}.{attr}"] = value
        
        return context


# 全局实体上下文实例（用于向后兼容）
# 推荐使用 pytest fixture 注入的方式
entity_context = EntityContext()
