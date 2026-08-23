"""按业务域定义的类型化 BDD 场景上下文。"""

from dataclasses import dataclass

from auto_tests.ui.bdd_ui.data_factory.entities import ClaimData, OrderData, ReviewData


@dataclass
class OrderScenarioContext:
    order: OrderData | None = None
    ui_status: str | None = None


@dataclass
class ClaimScenarioContext:
    claim: ClaimData | None = None
    previous_stage: str | None = None
    current_stage: str | None = None


@dataclass
class ReviewScenarioContext:
    review: ReviewData | None = None
    ui_status: str | None = None

