"""商品域 L3 Data Factory。"""

from __future__ import annotations

import uuid

from auto_tests.api.bdd_api.data_factory.entities.products import ProductEntity
from auto_tests.api.bdd_api.data_factory.specs.products import PRODUCT_DEFAULTS


class ProductFactory:
    @staticmethod
    def unique(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def build(self, **overrides) -> ProductEntity:
        values = {
            "sku": self.unique("AUTO_SKU"),
            "name": self.unique("AUTO_PRODUCT"),
            **PRODUCT_DEFAULTS,
            **overrides,
        }
        return ProductEntity(**values)
