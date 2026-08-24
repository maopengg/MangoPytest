"""Mango Mock UI 能力测试的公共组合入口。"""

from .base import MangoMockUICapabilityBase
from .business_preconditions import BusinessPreconditionMixin
from .element_cases import ElementCaseMixin
from .inventory_cases import InventoryCaseMixin
from .operation_cases import OperationCaseMixin


class MangoMockUICasePage(
    OperationCaseMixin,
    ElementCaseMixin,
    InventoryCaseMixin,
    BusinessPreconditionMixin,
    MangoMockUICapabilityBase,
):
    """组合独立的操作、控件与元素契约执行器。"""
