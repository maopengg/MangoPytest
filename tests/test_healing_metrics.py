"""元素自愈运行级统计与汇总落盘。"""

import json
from pathlib import Path

import pytest

from core.execution.pytest_evidence_plugin import _healing_summary_directory
from core.ui.healing_metrics import (
    HealingEvent,
    HealingMetricsRecorder,
    merge_summaries,
    summary_filename,
    write_summary,
)


@pytest.fixture(autouse=True)
def _isolate_global_recorder(monkeypatch):
    """汇总逻辑测试不污染全局累加器。"""

    import core.ui.healing_metrics as module

    monkeypatch.setattr(module, "healing_metrics", HealingMetricsRecorder())


def _event(**overrides) -> HealingEvent:
    value = {
        "element_name": "submit-button",
        "case_id": "test_x.py::test_y[CASE-1]",
        "used_source": "ai_accessibility",
        "used_ai": True,
        "temporary_heal_used": True,
        "final_score": 92,
        "model": "glm-4",
        "prompt_version": "web-snapshot-ref-v7",
    }
    value.update(overrides)
    return HealingEvent(**value)


def test_healed_requires_leaving_the_fixed_locator_path():
    assert _event(used_source="fixed_locator", used_ai=False,
                  temporary_heal_used=False).healed is False
    assert _event(used_source="fixed_locator", used_ai=False,
                  temporary_heal_used=True).healed is True
    assert _event().healed is True
    assert _event(operation_failed=True).healed_successfully is False


def test_snapshot_aggregates_by_source_and_element():
    recorder = HealingMetricsRecorder()
    recorder.record(_event(element_name="a"))
    recorder.record(_event(element_name="a", used_ai=False,
                           used_source="dom_text_candidate"))
    recorder.record(_event(element_name="b", used_source="fixed_locator",
                           used_ai=False, temporary_heal_used=False))
    recorder.record(_event(element_name="c", operation_failed=True))

    payload = recorder.snapshot()

    assert payload["operations"] == 4
    assert payload["healed_operations"] == 3
    assert payload["healed_successfully"] == 2
    assert payload["healed_failed"] == 1
    assert payload["ai_operations"] == 2
    assert payload["local_healed"] == 1
    assert payload["by_element"] == {"a": 2, "c": 1}
    assert payload["models"] == ["glm-4"]
    assert len(payload["events"]) == 4


def test_write_summary_skips_empty_and_writes_payload(tmp_path: Path, monkeypatch):
    import core.ui.healing_metrics as module

    assert write_summary(tmp_path) is None
    assert list(tmp_path.iterdir()) == []

    module.healing_metrics.record(_event())
    path = write_summary(tmp_path)

    assert path is not None and path.name == "ai-healing-summary.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["operations"] == 1
    assert payload["by_source"] == {"ai_accessibility": 1}


def test_summary_filename_distinguishes_workers(monkeypatch):
    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    assert summary_filename() == "ai-healing-summary.json"
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw2")
    assert summary_filename() == "ai-healing-summary-gw2.json"


def test_merge_summaries_combines_workers_and_tolerates_broken_files(tmp_path: Path):
    (tmp_path / "ai-healing-summary-gw0.json").write_text(json.dumps({
        "operations": 2, "healed_operations": 1, "healed_successfully": 1,
        "healed_failed": 0, "ai_operations": 1, "ai_healed_successfully": 1,
        "local_healed": 0, "by_source": {"ai_accessibility": 1},
        "by_element": {"a": 1}, "models": ["glm-4"], "prompt_versions": ["v7"],
    }), encoding="utf-8")
    (tmp_path / "ai-healing-summary-gw1.json").write_text(json.dumps({
        "operations": 3, "healed_operations": 2, "healed_successfully": 1,
        "healed_failed": 1, "ai_operations": 0, "ai_healed_successfully": 0,
        "local_healed": 2, "by_source": {"dom_text_candidate": 2},
        "by_element": {"a": 1, "b": 1}, "models": [], "prompt_versions": [],
    }), encoding="utf-8")
    (tmp_path / "ai-healing-summary-broken.json").write_text("{not json", encoding="utf-8")

    merged = merge_summaries(tmp_path)

    assert merged["operations"] == 5
    assert merged["healed_operations"] == 3
    assert merged["healed_failed"] == 1
    assert merged["ai_operations"] == 1
    assert merged["local_healed"] == 2
    assert merged["by_source"] == {"dom_text_candidate": 2, "ai_accessibility": 1}
    assert merged["by_element"] == {"a": 2, "b": 1}
    assert merged["models"] == ["glm-4"]
    # 无法解析的文件被跳过，不计入 workers（并集仍以有效文件为准）。
    assert merged["workers"] == [
        "ai-healing-summary-gw0.json", "ai-healing-summary-gw1.json",
    ]


def test_merge_summaries_returns_none_without_files(tmp_path: Path):
    assert merge_summaries(tmp_path) is None


class _FakeOption:
    def __init__(self, allure_report_dir=None):
        self.allure_report_dir = allure_report_dir


class _FakeConfig:
    def __init__(self, allure_report_dir=None):
        self.option = _FakeOption(allure_report_dir)


def test_healing_summary_directory_prefers_allure_sibling(tmp_path: Path):
    allure_dir = tmp_path / "run-1" / "allure-results"
    assert _healing_summary_directory(_FakeConfig(str(allure_dir))) == tmp_path / "run-1"

    fallback = _healing_summary_directory(_FakeConfig(None))
    assert fallback.name == "reports"
    assert fallback.is_absolute()
