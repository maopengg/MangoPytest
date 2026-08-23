"""故障注入域纯 pytest 用例。"""
import allure
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.http, allure.epic("Mango Mock API 自动化"), allure.feature("故障与场景")]
CASES = [
    ("FTAPI-0080 配置固定 HTTP 500 故障后调用目标接口", "fixed_http_failure"),
    ("FTAPI-0081 配置延迟故障后调用目标接口", "delayed_failure"),
    ("FTAPI-0082 配置仅前两次失败的最终成功场景", "eventual_success"),
    ("FTAPI-0083 按退避策略重试最终成功场景", "eventual_success_with_backoff"),
    ("FTAPI-0084 删除已启用故障后再次调用目标接口", "delete_fault_rule"),
    ("FTAPI-0085 准备不存在的场景编码", "reject_unknown_scenario"),
    ("FTAPI-0086 验证尚未执行完整步骤的场景", "verify_incomplete_scenario"),
    ("FTAPI-0087 完成场景全部动作后执行场景验证", "verify_completed_scenario"),
]

@pytest.mark.parametrize(("title", "method_name"), CASES, ids=[title.split()[0] for title, _ in CASES])
def test_fault_case(title, method_name, fault_service, assert_scenario):
    allure.dynamic.title(title)
    assert_scenario(getattr(fault_service, method_name)())
