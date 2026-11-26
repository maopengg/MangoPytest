"""AI 元素定位端到端验证（使用 fake model client，不访问真实模型服务）。

验证链路：固定定位器失效 → 本地确定性候选未命中 → 调用模型 → 用无障碍快照的
snapshot ref 解析出持久定位器 → 通过唯一性/可见性/语义校验 → 本次操作采用该定位器。

之所以必须用 fake client：真实网关需要凭据，而凭据禁止入库。fake client 只做一件事——
按可访问名从快照里挑 ref，等价于"模型看懂了释义"，因此能确定性地覆盖整条链路。
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil

import pytest

from mangoautomation.enums import ElementOperationEnum
from mangoautomation.models import ElementListModel, ElementModel

pytestmark = pytest.mark.ai_e2e

#: 页面上的目标按钮，其可访问名与元素描述**不同义**，以此逼出模型调用。
TARGET_ACCESSIBLE_NAME = "确认提交"
DECOY_ACCESSIBLE_NAME = "取消"

#: 元素描述：只用释义描述位置与用途，不含目标的可见文案。
PARAPHRASE = "位于报销单面板底部、用于完成审批流转的按钮"
#: 含目标的可见文案，本地确定性候选源即可命中，不应触发模型调用。
LITERAL = "位于报销单面板底部、显示「确认提交」的按钮"

HTML = f"""
<html><body>
<h1>报销单</h1>
<div id="panel">
  <button data-testid="cancel-claim">{DECOY_ACCESSIBLE_NAME}</button>
  <button data-testid="approve-claim">{TARGET_ACCESSIBLE_NAME}</button>
</div>
</body></html>
"""

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def _browser_executable() -> str | None:
    for path in CHROME_CANDIDATES:
        if Path(path).is_file():
            return path
    return None


class FakeModelClient:
    """按可访问名挑选 snapshot ref 的假模型客户端。"""

    model_name = "fake-model"

    def __init__(self, accessible_name: str = TARGET_ACCESSIBLE_NAME) -> None:
        self.accessible_name = accessible_name
        self.calls = 0
        self.prompts: list[dict] = []

    def complete_sync(self, messages, *, max_tokens, temperature, response_format=None) -> str:
        self.calls += 1
        payload = json.loads(messages[-1].get("content", "{}"))
        self.prompts.append(payload)
        tree = payload.get("accessibility_snapshot", {}).get("tree", "")
        for line in tree.splitlines():
            if f'"{self.accessible_name}"' not in line:
                continue
            match = re.search(r"\[ref=(e\d+)\]", line)
            if match:
                return json.dumps({
                    "schema_version": "snapshot-ref-v4",
                    "status": "matched",
                    "reason": "按释义选中审批流转按钮",
                    "candidates": [{
                        "source": "ai_accessibility",
                        "target_ref": match.group(1),
                        "reason": "面板内唯一的提交类按钮",
                        "confidence": 96,
                    }],
                }, ensure_ascii=False)
        return json.dumps({
            "schema_version": "snapshot-ref-v4",
            "status": "not_found",
            "reason": "快照中未找到符合释义的可操作节点",
            "candidates": [],
        }, ensure_ascii=False)


def _element(description: str, *, locator: str = "missing-approve-button") -> ElementModel:
    return ElementModel(
        id=9001, element_id=9001, type=ElementOperationEnum.OPE,
        name="approve-claim", category="报销业务区",
        description_template=description, element_version=1,
        ope_key="w_click", sleep=0,
        elements=[ElementListModel(
            exp=2, loc=f"get_by_test_id({locator!r})", prompt=description, slot=1,
        )],
    )


@pytest.fixture
def ai_page():
    """真实浏览器页面 + 带 fake 模型的 harness。"""

    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    from mangoautomation.element_healing import StaticRuntimeConfig, WebElementHealingHarness

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                headless=True, executable_path=_browser_executable()
            )
        except Exception as error:  # 没有可用浏览器时跳过，而不是让套件失败
            pytest.skip(f"无法启动浏览器：{error}")
        page = browser.new_page()
        page.set_content(HTML)

        def build(client: FakeModelClient, **runtime):
            return WebElementHealingHarness(
                model_client=client,
                runtime_config=StaticRuntimeConfig(
                    enabled=True, mode=2, semantic_strength_value=0,
                    fixed_retry_seconds_value=0, smart_timeout_seconds_value=20,
                    **runtime,
                ),
            )

        try:
            yield page, build
        finally:
            browser.close()


def _find(harness, page, element: ElementModel):
    return harness.locate_sync(
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


def test_ai_locates_element_when_fixed_locator_fails(ai_page) -> None:
    page, build = ai_page
    client = FakeModelClient()
    harness = build(client)

    result = _find(harness, page, _element(PARAPHRASE))

    assert result is not None, "AI 应能依据释义定位到目标按钮"
    assert client.calls == 1, "固定定位失效且确定性候选未命中时应恰好调用模型一次"
    metadata = result["metadata"]
    assert metadata["used_source"] == "ai_accessibility"
    assert metadata["used_ai"] is True
    assert metadata["temporary_heal_used"] is True
    assert metadata["trace"]["agent_called"] is True
    assert metadata["trace"]["model"] == "fake-model"
    # AI 命中后解析成可复用的持久定位器，并已通过唯一性校验。
    assert result["locator"].inner_text() == TARGET_ACCESSIBLE_NAME
    assert result["locator"].count() == 1


def test_ai_request_carries_the_configured_description_and_snapshot(ai_page) -> None:
    """请求体必须带上元素描述与无障碍快照——这是提示词真正生效的证据。"""

    page, build = ai_page
    client = FakeModelClient()
    harness = build(client)

    assert _find(harness, page, _element(PARAPHRASE)) is not None

    payload = client.prompts[0]
    assert payload["target"]["prompt"] == PARAPHRASE
    assert payload["target"]["name"] == "approve-claim"
    snapshot = payload["accessibility_snapshot"]
    assert snapshot["ref_engine"] == "playwright_aria"
    assert TARGET_ACCESSIBLE_NAME in snapshot["tree"]
    assert snapshot["snapshot_id"]


def test_local_deterministic_candidates_avoid_model_cost(ai_page) -> None:
    """描述里带了可见文案时，本地候选即可命中，不应调用模型。"""

    page, build = ai_page
    client = FakeModelClient()
    harness = build(client)

    result = _find(harness, page, _element(LITERAL))

    assert result is not None
    assert client.calls == 0, "本地确定性候选命中时不应产生模型费用"
    assert result["metadata"]["used_ai"] is False


def test_model_not_found_surfaces_a_reason(ai_page) -> None:
    """模型判定未命中时，调用方应能拿到可解释的失败原因。

    注意：没有产生任何候选，所以 ``reject_reasons`` 为空；原因落在
    ``agent_candidates`` 阶段的 error 上（``_locator_failure`` 会据此生成用户文案）。
    """

    page, build = ai_page
    client = FakeModelClient(accessible_name="不存在的按钮")
    harness = build(client)

    assert _find(harness, page, _element(PARAPHRASE)) is None
    assert client.calls == 1

    attempt = harness.get_last_attempt(9001)
    assert attempt["used_source"] == "candidate_exhausted"
    assert attempt["used_ai"] is True
    assert attempt["reject_reasons"] == []
    assert attempt["trace"]["decision"]["status"] == "rejected"
    agent_stage = next(
        stage for stage in attempt["trace"]["stages"] if stage["name"] == "agent_candidates"
    )
    assert "未找到符合释义" in agent_stage["error"]


def test_vision_fallback_is_off_unless_explicitly_enabled(ai_page) -> None:
    """视觉兜底默认关闭：standalone 无法开启它，必须显式装配。"""

    page, build = ai_page
    harness = build(FakeModelClient())
    assert harness.visual_locator_enabled() is False
    assert harness.visual_agent is None
