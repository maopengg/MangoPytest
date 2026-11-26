from core.execution.data_lineage import (
    current_lineage,
    instrument_lineage_object,
    start_lineage,
    stop_lineage,
)


class DemoFactory:
    def product(self):
        return {"sku": "AUTO_SKU", "name": "AUTO_PRODUCT"}

    @staticmethod
    def order(product_id: int):
        return {"items": [{"product_id": product_id, "quantity": 1}]}


class DemoRepository:
    def create_product(self, payload):
        return {"code": 0, "data": {"id": 101, **payload}}

    def create_order(self, payload):
        return {"code": 0, "data": {"id": 202, **payload}}

    def delete_product(self, product_id):
        return {"code": 0, "data": {"id": product_id}}


def test_lineage_tracks_factory_repository_relations_and_cleanup() -> None:
    factory, repository = DemoFactory(), DemoRepository()
    start_lineage("tests/test_demo.py::test_order")
    try:
        instrument_lineage_object(factory)
        instrument_lineage_object(repository)
        product_payload = factory.product()
        product = repository.create_product(product_payload)["data"]
        order_payload = factory.order(product["id"])
        repository.create_order(order_payload)
        repository.delete_product(product["id"])
        graph = current_lineage().export()
    finally:
        stop_lineage()

    assert graph["summary"] == {"factories": 2, "operations": 3, "entities": 2, "relations": 6}
    product_node = next(
        node for node in graph["nodes"]
        if node["kind"] == "entity" and node["entity_type"] == "product"
    )
    assert product_node["entity_id"] == "101"
    assert product_node["status"] == "deleted"
    assert any(edge["relation"] == "被引用" for edge in graph["edges"])
