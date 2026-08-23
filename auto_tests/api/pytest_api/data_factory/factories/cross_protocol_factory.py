"""跨协议场景 L3 Data Factory。"""

from auto_tests.api.pytest_api.data_factory.entities.cross_protocol import CrossProtocolEntity
from auto_tests.api.pytest_api.repositories.cross_protocol import CrossProtocolRepository


class CrossProtocolFactory:
    def __init__(self, repository: CrossProtocolRepository):
        self.repository = repository

    def create_claim_http(self, entity: CrossProtocolEntity) -> dict:
        return self.repository.create_claim_http(entity.claim_payload())

    def create_claim_mcp(self, entity: CrossProtocolEntity) -> dict:
        return self.repository.create_claim_mcp(entity.claim_payload())

    def create_claim_grpc(self, entity: CrossProtocolEntity):
        return self.repository.create_claim_grpc(entity.claim_payload())

    def start_review_http(self, entity: CrossProtocolEntity) -> dict:
        return self.repository.start_review_http(entity.review_payload())

    def start_review_grpc(self, entity: CrossProtocolEntity):
        return self.repository.start_review_grpc(entity.review_payload())
