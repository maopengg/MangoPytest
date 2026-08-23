"""兼容现有能力测试的轻量组合入口。"""

from .base import PytestUICapabilityBase
from .business_preconditions import BusinessPreconditionMixin
from .element_cases import ElementCaseMixin
from .inventory_cases import InventoryCaseMixin
from .operation_cases import OperationCaseMixin


class PytestUICasePage(
    OperationCaseMixin,
    ElementCaseMixin,
    InventoryCaseMixin,
    BusinessPreconditionMixin,
    PytestUICapabilityBase,
):
    """组合独立能力执行器，保留原测试入口。"""

