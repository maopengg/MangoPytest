"""按业务域拆分的 UI 页面对象。"""

from .claims import ClaimPage
from .orders import OrderPage
from .reviews import ReviewPage

__all__ = ["ClaimPage", "OrderPage", "ReviewPage"]

