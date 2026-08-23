"""商品域 L4 Service：编排数据工厂和 Repository。"""

from auto_tests.api.pytest_api.data_factory.factories.product_factory import ProductFactory
from auto_tests.api.pytest_api.repositories.products import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository, factory: ProductFactory):
        self.repository = repository
        self.factory = factory

    def create(self, **overrides):
        return self.repository.create(self.factory.build(**overrides))

    def create_duplicate(self):
        entity = self.factory.build()
        return self.repository.create(entity), self.repository.create(entity)

    def search_by_name(self):
        keyword = self.factory.unique("AUTO_MATCH")
        matched = self.repository.create(self.factory.build(name=f"{keyword}_PRODUCT"))
        other = self.repository.create(self.factory.build())
        return matched, other, self.repository.search(keyword), keyword

    def update_current_version(self):
        created = self.create().json()["data"]
        response = self.repository.update_price(created["id"], 22.5, created["version"])
        return created, response

    def update_stale_version(self):
        created = self.create().json()["data"]
        first = self.repository.update_price(created["id"], 22.5, created["version"])
        stale = self.repository.update_price(created["id"], 33.5, created["version"])
        return first, stale

    def delete_then_search(self):
        created = self.create().json()["data"]
        deleted = self.repository.delete(created["id"])
        return deleted, self.repository.search(created["sku"])
