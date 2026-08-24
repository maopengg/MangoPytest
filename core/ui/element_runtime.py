"""Bridge local/Feishu element rows to mangoautomation's element runtime."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
import os
from typing import Any, Protocol

import allure
from mangoautomation.element_healing import WebElementHealingHarness
from mangoautomation.enums import DriveTypeEnum, ElementExpEnum, ElementOperationEnum
from mangoautomation.exceptions import MangoAutomationError
from mangoautomation.models import (
    ElementListModel,
    ElementModel,
    ElementResultModel,
    MethodModel,
)
from mangoautomation.uidrives import BaseData, SyncElement
from mangotools.enums import StatusEnum
from playwright.sync_api import Locator

from core.execution.evidence import attach_json
from core.sources.element_schema import CANONICAL_ELEMENT_HEADERS

_EXPRESSIONS = {
    "XPATH": ElementExpEnum.XPATH.value,
    "0": ElementExpEnum.XPATH.value,
    "TEST_ID": ElementExpEnum.LOCATOR.value,
    "TESTID": ElementExpEnum.LOCATOR.value,
    "1": ElementExpEnum.LOCATOR.value,
    "LOCATOR": ElementExpEnum.LOCATOR.value,
    "定位器": ElementExpEnum.LOCATOR.value,
    "2": ElementExpEnum.LOCATOR.value,
    "TEXT": ElementExpEnum.TEXT.value,
    "文本": ElementExpEnum.TEXT.value,
    "3": ElementExpEnum.TEXT.value,
    "PLACEHOLDER": ElementExpEnum.PLACEHOLDER.value,
    "占位符": ElementExpEnum.PLACEHOLDER.value,
    "4": ElementExpEnum.PLACEHOLDER.value,
    "CSS": ElementExpEnum.CSS.value,
    "9": ElementExpEnum.CSS.value,
}


def _value(record: dict[str, Any], canonical: str, *aliases: str, default=None):
    for key in (canonical, *aliases):
        value = record.get(key)
        if value not in (None, ""):
            return value
    return default


def _optional_int(value: Any) -> int | None:
    return None if value in (None, "") else int(value)


def _optional_text(value: Any) -> str | None:
    return None if value in (None, "") else str(value)


def _bool(value: Any, *, default: bool = False) -> bool:
    if value in (None, ""):
        return default
    return str(value).strip().lower() in {"是", "true", "1", "yes", "启用"}


def _expression_type(value: str | int) -> int:
    key = str(value).strip().upper()
    if key not in _EXPRESSIONS:
        raise ValueError(f"不支持的定位方式: {value}")
    return _EXPRESSIONS[key]


def _runtime_expression(method: str | int, expression: str) -> tuple[int, str]:
    exp = _expression_type(method)
    value = str(expression).strip()
    if str(method).strip().upper() in {"TEST_ID", "TESTID", "1"}:
        return exp, f"get_by_test_id({value!r})"
    if exp == ElementExpEnum.XPATH.value and value.startswith("xpath="):
        value = value.removeprefix("xpath=")
    return exp, value


@dataclass(frozen=True)
class LocatorDefinition:
    method: str | int
    expression: str
    index: int | None = None
    is_iframe: bool = False
    prompt: str | None = None
    slot: int = 1

    def to_model(self) -> ElementListModel:
        exp, loc = _runtime_expression(self.method, self.expression)
        # Demo Excel historically used Playwright's zero-based nth index. The
        # mangoautomation model uses 1 for the first element and 0 for no nth.
        sub = self.index + 1 if self.index is not None else None
        return ElementListModel(
            exp=exp,
            loc=loc,
            sub=sub,
            is_iframe=StatusEnum.SUCCESS.value if self.is_iframe else StatusEnum.FAIL.value,
            prompt=self.prompt,
            slot=self.slot,
        )


@dataclass(frozen=True)
class ElementDefinition:
    element_id: int
    project_name: str
    module_name: str
    page_name: str
    name: str
    locators: tuple[LocatorDefinition, ...]
    category: str | None = None
    ai_heal_status: int = 1
    collect_snapshot: bool = True
    sleep: int | None = None
    tag: str | None = None
    input_type: str | None = None
    role: str | None = None
    description: str | None = None
    interactive: bool = False
    disabled: bool = False

    @property
    def locating_method(self) -> str | int:
        return self.locators[0].method

    @property
    def expression(self) -> str:
        return self.locators[0].expression

    @property
    def index(self) -> int | None:
        return self.locators[0].index

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "ElementDefinition":
        locators = []
        for slot in range(1, 4):
            method = _value(record, f"定位方式{slot}", f"类型-{slot}", f"*类型-{slot}")
            expression = _value(
                record,
                f"定位表达式{slot}",
                f"表达式{slot}",
                f"定位-{slot}",
                f"*定位-{slot}",
            )
            if method in (None, "") or expression in (None, ""):
                continue
            locators.append(
                LocatorDefinition(
                    method=method,
                    expression=str(expression),
                    index=_optional_int(
                        _value(record, f"元素下标{slot}", f"下标{slot}", f"元素下标-{slot}")
                    ),
                    is_iframe=_bool(
                        _value(record, f"是否iframe{slot}", "是否iframe", "iframe")
                    ),
                    prompt=_optional_text(
                        _value(record, f"AI定位提示词{slot}", "AI定位提示词", "提示词")
                    ),
                    slot=slot,
                )
            )
        if not locators:
            raise ValueError(f"元素 {_value(record, '元素名称', '*元素名称')} 没有有效定位表达式")
        return cls(
            element_id=int(_value(record, "ID", "元素ID")),
            project_name=str(_value(record, "项目名称", default="")),
            module_name=str(_value(record, "模块名称", default="")),
            page_name=str(_value(record, "页面名称", default="")),
            name=str(_value(record, "元素名称", "*元素名称")),
            locators=tuple(locators),
            category=_optional_text(_value(record, "元素分类", "分类")),
            ai_heal_status=int(_bool(_value(record, "AI自愈状态"), default=True)),
            collect_snapshot=_bool(_value(record, "采集快照"), default=True),
            sleep=_optional_int(_value(record, "等待时间")),
            tag=_optional_text(record.get("标签")),
            input_type=_optional_text(record.get("input类型")),
            role=_optional_text(record.get("role")),
            description=_optional_text(record.get("说明")),
            interactive=_bool(record.get("可交互")),
            disabled=_bool(record.get("禁用")),
        )

    def to_element_model(
        self,
        *,
        operation_type: ElementOperationEnum,
        method: str,
        arguments: list[MethodModel],
        locators: tuple[LocatorDefinition, ...] | None = None,
    ) -> ElementModel:
        return ElementModel(
            id=self.element_id,
            element_id=self.element_id,
            type=operation_type,
            name=self.name,
            category=self.category or self.page_name or self.module_name,
            ai_heal_status=self.ai_heal_status,
            collect_snapshot=self.collect_snapshot,
            elements=[item.to_model() for item in (locators or self.locators)],
            sleep=self.sleep,
            ope_key=method,
            ope_value=arguments,
        )


class ElementRepository(Protocol):
    def get(self, name: str, *args, **kwargs) -> ElementDefinition: ...


class ElementRuntime:
    """Execute named elements through SyncElement and retain structured results."""

    def __init__(self, base_data: BaseData, repository: ElementRepository, settings=None):
        self.base_data = base_data
        self.repository = repository
        self.driver = SyncElement(base_data, DriveTypeEnum.WEB.value)
        self.last_result: ElementResultModel | None = None
        self._configure_healing(settings)

    def _configure_healing(self, settings) -> None:
        enabled = bool(getattr(settings, "ELEMENT_HEALING_ENABLED", True))
        if not enabled or self.base_data.locator_engine is not None:
            return
        ai_enabled = bool(getattr(settings, "AI_ELEMENT_HEALING_ENABLED", False))
        api_key = str(getattr(settings, "AI_API_KEY", "") or os.getenv("MANGO_AI_API_KEY", ""))
        engine = WebElementHealingHarness.standalone(
            api_key=api_key if ai_enabled else None,
            base_url=str(getattr(settings, "AI_BASE_URL", "https://api.siliconflow.cn/v1")),
            model=str(getattr(settings, "AI_MODEL", "THUDM/GLM-Z1-9B-0414")),
            mode=int(getattr(settings, "ELEMENT_HEALING_MODE", 2)),
            logger=self.base_data.log,
        )
        self.base_data.set_locator_engine(engine)
        self.base_data.is_ai = bool(ai_enabled and api_key)

    def locator(self, name: str) -> Locator:
        """Resolve a Locator via mangoautomation for compatibility-only page reads."""
        definition = self.repository.get(name)
        locator_model = definition.locators[0].to_model()
        locator, _, _ = self.driver.web_find_element(
            definition.name,
            ElementOperationEnum.OPE.value,
            locator_model.exp,
            locator_model.loc,
            locator_model.sub,
            locator_model.is_iframe,
        )
        return locator

    def execute(
        self,
        name: str,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        assertion: bool = False,
        target_names: tuple[str, ...] = (),
    ) -> ElementResultModel:
        definition = self.repository.get(name)
        all_definitions = (definition, *(self.repository.get(item) for item in target_names))
        operation_type = ElementOperationEnum.ASS if assertion else ElementOperationEnum.OPE
        arguments = self._arguments(method, params or {}, assertion, len(all_definitions))
        locators = (
            definition.locators
            if not target_names
            else tuple(item.locators[0] for item in all_definitions)
        )
        model = definition.to_element_model(
            operation_type=operation_type,
            method=method,
            arguments=arguments,
            locators=locators,
        )
        with allure.step(f"UI 元素 · {definition.name} · {method}"):
            attach_json("操作信息", model.model_dump(mode="json"))
            result = self.driver.element_main(model)
            attach_json("操作结果", result.model_dump(mode="json"))
        self.last_result = result
        history = getattr(self.base_data, "ui_element_results", None)
        if history is None:
            history = []
            self.base_data.ui_element_results = history
        history.append(result)
        if result.status != StatusEnum.SUCCESS.value:
            raise MangoAutomationError(300, result.error_message or f"元素 {name} 执行失败")
        return result

    def _arguments(
        self,
        method: str,
        params: dict[str, Any],
        assertion: bool,
        locator_count: int,
    ) -> list[MethodModel]:
        owner = self.driver.web_assertion_element if assertion else getattr(self.driver, method)
        signature = inspect.signature(
            getattr(type(self.driver), method, owner) if not assertion else owner
        )
        locator_fields = ["actual"] if assertion else [
            name for name in signature.parameters if name.startswith("locating")
        ]
        if len(locator_fields) < locator_count:
            raise ValueError(f"{method} 只接受 {len(locator_fields)} 个元素，实际传入 {locator_count} 个")
        values = [MethodModel(f=name, v=None) for name in locator_fields[:locator_count]]
        values.extend(MethodModel(f=key, v=value) for key, value in params.items())
        return values


def element_runtime(base_data: BaseData, repository: ElementRepository, settings=None) -> ElementRuntime:
    runtimes = getattr(base_data, "_named_element_runtimes", None)
    if runtimes is None:
        runtimes = {}
        base_data._named_element_runtimes = runtimes
    key = id(repository)
    if key not in runtimes:
        runtimes[key] = ElementRuntime(base_data, repository, settings)
    return runtimes[key]
