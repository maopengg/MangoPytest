"""多个实体组成的场景对象。"""

from dataclasses import dataclass

from ..entities import OrderData, RunData


@dataclass(frozen=True)
class OrderScenario:
    run: RunData
    order: OrderData

