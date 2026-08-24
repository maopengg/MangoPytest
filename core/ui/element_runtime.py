"""Bridge local/Feishu element rows to mangoautomation's element runtime."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
import os
import time
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
    description: str | None = None

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
            description=_optional_text(record.get("说明")),
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
            category=self.page_name or self.module_name,
            elements=[item.to_model() for item in (locators or self.locators)],
            sleep=None,
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
            timeout=int(getattr(settings, "AI_TIMEOUT", 30)),
            mode=int(getattr(settings, "ELEMENT_HEALING_MODE", 2)),
            semantic_strength=int(getattr(settings, "AI_SEMANTIC_STRENGTH", 0)),
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
        operation_context = {
            "method": method,
            "input": {
                "operation": method,
                "arguments": [],
                "keyword_arguments": params or {},
            },
        }
        missing = object()
        previous_context = getattr(
            self.base_data, "_ui_operation_evidence_context", missing
        )
        self.base_data._ui_operation_evidence_context = operation_context
        started = time.perf_counter()
        try:
            with allure.step(f"UI 操作 · {method} · {definition.name}"):
                try:
                    result = self.driver.element_main(model)
                except Exception as error:
                    attach_json(
                        "操作信息",
                        self._operation_input_evidence(operation_context, all_definitions),
                    )
                    attach_json("操作结果", {
                        "status": "failed",
                        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                        "page_url": getattr(
                            getattr(self.base_data, "page", None), "url", ""
                        ),
                        "error_type": type(error).__name__,
                        "error": str(error),
                    })
                    raise
                attach_json(
                    "操作信息",
                    self._operation_input_evidence(operation_context, all_definitions),
                )
                attach_json("操作结果", {
                    "status": (
                        "passed"
                        if result.status == StatusEnum.SUCCESS.value
                        else "failed"
                    ),
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "page_url": getattr(getattr(self.base_data, "page", None), "url", ""),
                    "element_result": result.model_dump(mode="json"),
                })
        finally:
            if previous_context is missing:
                delattr(self.base_data, "_ui_operation_evidence_context")
            else:
                self.base_data._ui_operation_evidence_context = previous_context
        self.last_result = result
        history = getattr(self.base_data, "ui_element_results", None)
        if history is None:
            history = []
            self.base_data.ui_element_results = history
        history.append(result)
        if result.status != StatusEnum.SUCCESS.value:
            raise MangoAutomationError(300, result.error_message or f"元素 {name} 执行失败")
        return result

    @classmethod
    def _operation_input_evidence(
        cls,
        operation_context: dict[str, Any],
        definitions: tuple[ElementDefinition, ...],
    ) -> dict[str, Any]:
        operation_input = operation_context["input"]
        operation_input["named_elements"] = [
            cls._definition_evidence(item) for item in definitions
        ]
        return operation_input

    @staticmethod
    def _definition_evidence(definition: ElementDefinition) -> dict[str, Any]:
        return {
            "id": definition.element_id,
            "project_name": definition.project_name,
            "module_name": definition.module_name,
            "page_name": definition.page_name,
            "name": definition.name,
            "description": definition.description,
            "locators": [
                {
                    "slot": locator.slot,
                    "method": locator.method,
                    "expression": locator.expression,
                    "index": locator.index,
                    "ai_prompt": locator.prompt,
                }
                for locator in definition.locators
            ],
        }

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
