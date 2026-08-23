"""兼容旧导入，实际实现已按业务域拆分。"""

from .bundle import BddUIRepositories

BddUIMockRepository = BddUIRepositories

__all__ = ["BddUIMockRepository", "BddUIRepositories"]
