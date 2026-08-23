"""L2 按业务域组织的 Repository。"""

from .cross_protocol import CrossProtocolRepository
from .functional_cases import FunctionalCaseRepository

__all__ = ["CrossProtocolRepository", "FunctionalCaseRepository"]
