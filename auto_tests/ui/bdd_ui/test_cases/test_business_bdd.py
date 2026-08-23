"""绑定真实中文业务 UI Feature。"""

from pytest_bdd import scenarios

scenarios(
    "../features/business/orders.feature",
    "../features/business/claims.feature",
    "../features/business/reviews.feature",
)
