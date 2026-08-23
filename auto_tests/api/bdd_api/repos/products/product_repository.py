"""商品域 L2 Repository，集中维护商品接口路径和协议细节。"""

from __future__ import annotations

import httpx

from auto_tests.api.bdd_api.data_factory.entities.products import ProductEntity
from auto_tests.api.bdd_api.repos.functional_cases import FunctionalCaseRepository


class ProductRepository:
    def __init__(self, gateway: FunctionalCaseRepository):
        self.gateway = gateway

    def create(self, product: ProductEntity) -> httpx.Response:
        return self.gateway.request(
            "POST", "/api/v1/products", json=product.create_payload()
        )

    def search(self, keyword: str) -> httpx.Response:
        return self.gateway.request(
            "GET", "/api/v1/products", params={"keyword": keyword}
        )

    def update_price(
        self, product_id: int, *, price: float, version: int
    ) -> httpx.Response:
        return self.gateway.request(
            "PATCH",
            f"/api/v1/products/{product_id}",
            json={"price": price, "version": version},
        )

    def delete(self, product_id: int) -> httpx.Response:
        return self.gateway.request("DELETE", f"/api/v1/products/{product_id}")
