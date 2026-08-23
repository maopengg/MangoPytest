"""跨协议测试数据规格。"""

from auto_tests.api.bdd_api.data_factory.entities.cross_protocol import CrossProtocolEntity


def cross_protocol_spec(**overrides) -> CrossProtocolEntity:
    values = CrossProtocolEntity().model_dump()
    values.update(overrides)
    return CrossProtocolEntity(**values)
