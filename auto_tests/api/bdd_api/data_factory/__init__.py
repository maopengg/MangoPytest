"""L3 数据工厂统一出口。"""

from auto_tests.api.bdd_api.data_factory.entities.cross_protocol import CrossProtocolEntity
from auto_tests.api.bdd_api.data_factory.entities.functional_case import FunctionalCaseResult
from auto_tests.api.bdd_api.data_factory.factories import (
    CrossProtocolFactory,
    FunctionalCaseFactory,
)

__all__ = [
    "CrossProtocolEntity",
    "FunctionalCaseResult",
    "CrossProtocolFactory",
    "FunctionalCaseFactory",
]
