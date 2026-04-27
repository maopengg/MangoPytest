# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据工厂管理器
# @Time   : 2026-03-31
# @Author : 毛鹏
import threading
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class DataDependency:
    """数据依赖关系"""
    module_name: str
    dependencies: List[str]  # 依赖的模块列表
    factory_method: str  # 创建数据的方法名
    cleanup_method: str  # 清理数据的方法名


class DataFactoryManager:
    """数据工厂管理器 - 负责管理模块依赖关系和数据生命周期"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.dependencies: Dict[str, DataDependency] = {}
            self.created_data: Dict[str, Dict[str, Any]] = {}
            self._initialized = True

    def register_dependency(self, module_name: str, dependencies: List[str],
                            factory_method: str, cleanup_method: str):
        """注册模块依赖关系"""
        self.dependencies[module_name] = DataDependency(
            module_name=module_name,
            dependencies=dependencies,
            factory_method=factory_method,
            cleanup_method=cleanup_method
        )

    def get_dependency_order(self, target_module: str) -> List[str]:
        """获取依赖创建顺序（拓扑排序）"""
        visited = set()
        result = []

        def dfs(module: str):
            if module in visited:
                return
            visited.add(module)

            if module in self.dependencies:
                for dep in self.dependencies[module].dependencies:
                    dfs(dep)

            result.append(module)

        dfs(target_module)
        return result

    def create_data_for_module(self, module_name: str, factory_instance, **kwargs) -> Dict[str, Any]:
        """为指定模块创建所有依赖数据"""
        if module_name not in self.dependencies:
            raise ValueError(f"未注册的模块: {module_name}")

        # 获取依赖创建顺序
        creation_order = self.get_dependency_order(module_name)

        created_data = {}

        for dep_module in creation_order:
            if dep_module not in self.created_data:
                # 调用对应的工厂方法创建数据
                factory_method = getattr(factory_instance, self.dependencies[dep_module].factory_method)
                data = factory_method(**kwargs)
                self.created_data[dep_module] = data
                created_data[dep_module] = data

        return created_data

    def cleanup_data_for_module(self, module_name: str, factory_instance):
        """清理指定模块的所有数据"""
        if module_name not in self.dependencies:
            return

        # 获取依赖清理顺序（反向）
        cleanup_order = self.get_dependency_order(module_name)[::-1]

        for dep_module in cleanup_order:
            if dep_module in self.created_data:
                # 调用对应的清理方法
                cleanup_method = getattr(factory_instance, self.dependencies[dep_module].cleanup_method)
                cleanup_method(self.created_data[dep_module])
                del self.created_data[dep_module]

    def get_created_data(self, module_name: str) -> Optional[Dict[str, Any]]:
        """获取已创建的数据"""
        return self.created_data.get(module_name)


# 全局数据工厂管理器实例
data_factory_manager = DataFactoryManager()
