"""pytest_ui 独立 Repository 层。"""

from .bundle import PytestUIRepositories
from .mango_mock import PytestUIMockRepository

__all__ = ["PytestUIMockRepository", "PytestUIRepositories"]
