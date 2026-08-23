"""跨协议测试数据准备步骤，只通过 Data Factory 创建。"""

from pytest_bdd import given

from auto_tests.api.bdd_api.data_factory.factories import CrossProtocolFactory


@given("使用 HTTP 工厂创建大额报销")
def create_claim_by_http(cross_protocol_factory, cross_protocol_entity, scenario_context):
    claim = cross_protocol_factory.create_claim_http(cross_protocol_entity)
    scenario_context.update(claim_id=claim["id"], claim=claim)


@given("使用 MCP 工厂创建大额报销")
def create_claim_by_mcp(cross_protocol_factory, cross_protocol_entity, scenario_context):
    claim = cross_protocol_factory.create_claim_mcp(cross_protocol_entity)
    scenario_context.update(claim_id=claim["id"], claim=claim)


@given("使用 gRPC 工厂创建大额报销")
def create_claim_by_grpc(cross_protocol_factory, cross_protocol_entity, scenario_context):
    claim = cross_protocol_factory.create_claim_grpc(cross_protocol_entity)
    scenario_context.update(claim_id=claim.claim_id, claim=claim)


@given("使用 HTTP 工厂启动合同审查")
def start_review_by_http(cross_protocol_factory, cross_protocol_entity, scenario_context):
    review = cross_protocol_factory.start_review_http(cross_protocol_entity)
    scenario_context.update(job_id=review["id"], review=review)


@given("使用 gRPC 工厂启动合同审查")
def start_review_by_grpc(cross_protocol_factory, cross_protocol_entity, scenario_context):
    review = cross_protocol_factory.start_review_grpc(cross_protocol_entity)
    scenario_context.update(job_id=review.job_id, review=review)


@given("两个 Test Run 使用相同业务标识创建报销")
def create_same_business_identifier(
    cross_protocol_factory,
    cross_protocol_entity,
    secondary_repository,
    scenario_context,
):
    secondary_factory = CrossProtocolFactory(secondary_repository)
    claim_a = cross_protocol_factory.create_claim_http(cross_protocol_entity)
    claim_b = secondary_factory.create_claim_http(cross_protocol_entity)
    scenario_context.update(
        claim_id=claim_a["id"],
        claim_a=claim_a,
        claim_b=claim_b,
        secondary_repository=secondary_repository,
    )
