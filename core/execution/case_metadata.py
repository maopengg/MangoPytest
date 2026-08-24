"""全项目统一的 Allure Case 分类与命名规范。"""

from __future__ import annotations

import re

import allure


CASE_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3,4}$")


def apply_case_metadata(
    *,
    case_id: str,
    title: str,
    epic: str,
    feature: str,
    story: str | None = None,
) -> None:
    """给参数化 Case 设置稳定、可分组且可读的 Allure 元数据。"""
    normalized_id = str(case_id).strip()
    normalized_title = str(title).strip()
    if not CASE_ID_PATTERN.fullmatch(normalized_id):
        raise ValueError(f"Case ID 不符合全局规范：{case_id}")
    if not normalized_title or normalized_title.startswith("test_"):
        raise ValueError(f"Case 标题必须是可读业务名称：{title}")
    for label, value in (("Epic", epic), ("Feature", feature)):
        if not str(value).strip():
            raise ValueError(f"{label} 不能为空")

    allure.dynamic.id(normalized_id)
    allure.dynamic.epic(str(epic).strip())
    allure.dynamic.feature(str(feature).strip())
    if story and str(story).strip():
        allure.dynamic.story(str(story).strip())
    allure.dynamic.title(f"{normalized_id} {normalized_title}")


__all__ = ["CASE_ID_PATTERN", "apply_case_metadata"]
