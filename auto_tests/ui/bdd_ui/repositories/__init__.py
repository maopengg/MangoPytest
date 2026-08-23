"""bdd_ui 独立 Repository 层。"""

from .bundle import BddUIRepositories
from .mango_mock import BddUIMockRepository

__all__ = ["BddUIMockRepository", "BddUIRepositories"]
