"""兼容现有能力测试的轻量组合入口。"""

from .base import BddUICapabilityBase
from .business_preconditions import BusinessPreconditionMixin
from .element_cases import ElementCaseMixin
from .inventory_cases import InventoryCaseMixin
from .operation_cases import OperationCaseMixin


class BddUICasePage(
    OperationCaseMixin,
    ElementCaseMixin,
    InventoryCaseMixin,
    BusinessPreconditionMixin,
    BddUICapabilityBase,
):
    """组合独立能力执行器，保留原测试入口。"""

