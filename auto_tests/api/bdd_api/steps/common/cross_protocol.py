"""跨协议场景通用步骤。"""

from pytest_bdd import given

from core.utils import log


@given("已创建跨协议隔离测试运行")
def isolated_test_run(cross_protocol_repository):
    log.debug(f"使用 Test Run: {cross_protocol_repository.run_id}")

