"""AI 元素定位真实网关冒烟测试。

默认**跳过**：真实凭据禁止入库（``AGENTS.md``），只允许通过环境变量或 CI Secret 注入。
需要验证时显式提供：

```bash
AI_API_KEY=sk-xxx AI_ELEMENT_HEALING_ENABLED=true \\
    ENV=test .venv/bin/python -m pytest tests/test_ai_element_locating_smoke.py -q
```

本用例只验证"网关可用 + 提示词可解析 + 响应满足 schema + 链路不抛错"，
不断言模型一定选中目标——真实模型存在不确定性，把"必须命中"写成断言会让
冒烟测试长期不稳定。命中时额外校验选中的确实是目标元素。
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mangoautomation.enums import ElementOperationEnum
from mangoautomation.models import ElementListModel, ElementModel

pytestmark = [pytest.mark.ai_e2e, pytest.mark.ai_smoke]

TARGET_ACCESSIBLE_NAME = "确认提交"
DESCRIPTION = "位于报销单面板底部、用于完成审批流转的按钮"

HTML = f"""
<html><body>
<h1>报销单</h1>
<div id="panel">
  <button data-testid="cancel-claim">取消</button>
  <button data-testid="approve-claim">{TARGET_ACCESSIBLE_NAME}</button>
</div>
</body></html>
"""

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def _browser_executable() -> str | None:
    return next((path for path in CHROME_CANDIDATES if Path(path).is_file()), None)


@pytest.fixture
def real_gateway_harness():
    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        pytest.skip("未提供 AI_API_KEY（凭据禁止入库，需由环境变量或 CI Secret 注入）")

    from mangoautomation.element_healing import WebElementHealingHarness

    return WebElementHealingHarness.standalone(
        api_key=api_key,
        base_url=os.getenv("AI_BASE_URL", "https://api.siliconflow.cn/v1"),
        model=os.getenv("AI_MODEL", "THUDM/GLM-Z1-9B-0414"),
        timeout=int(os.getenv("AI_TIMEOUT", "30")),
        mode=2,
        semantic_strength=0,
    )


def test_real_gateway_returns_a_usable_locator(real_gateway_harness) -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

    element = ElementModel(
        id=9101, element_id=9101, type=ElementOperationEnum.OPE,
        name="approve-claim", category="报销业务区",
        description_template=DESCRIPTION, element_version=1,
        ope_key="w_click", sleep=0,
        elements=[ElementListModel(
            exp=2, loc="get_by_test_id('missing-approve-button')",
            prompt=DESCRIPTION, slot=1,
        )],
    )

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                headless=True, executable_path=_browser_executable()
            )
        except Exception as error:
            pytest.skip(f"无法启动浏览器：{error}")
        page = browser.new_page()
        page.set_content(HTML)
        try:
            result = real_gateway_harness.locate_sync(
                page, element, None, [element.elements[0].loc],
                {
                    "ope_key": "w_click",
                    "type": ElementOperationEnum.OPE.value,
                    "exp": 2,
                    "loc": element.elements[0].loc,
                    "sub": None,
                },
                RuntimeError("locator not found"),
            )
        finally:
            browser.close()

    # 无论是否命中，模型都必须真的被调用过（否则说明凭据/网关配置没生效）。
    attempt = real_gateway_harness.get_last_attempt(9101)
    assert attempt, "未产生自愈尝试记录，说明链路没有跑起来"
    assert attempt["trace"]["agent_called"] is True, "模型未被调用，请检查网关与凭据"
    assert attempt["trace"]["model"], "响应中缺少模型名，说明未走到模型调用"

    if result is not None:
        assert result["metadata"]["used_ai"] is True
        assert result["locator"].count() == 1
        assert result["locator"].inner_text() == TARGET_ACCESSIBLE_NAME
