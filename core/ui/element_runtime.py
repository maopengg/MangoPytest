"""Bridge local/Feishu element rows to mangoautomation's element runtime."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import inspect
import json
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
from core.sources.page_labels import page_display_name
from core.sources.prompt_spec import merge_prompt_columns
from core.ui.healing_metrics import (
    FIXED_LOCATOR_SOURCE,
    HealingEvent,
    healing_metrics,
)

#: 提示词为空时，允许用元素表的"说明"列兜底作为 AI 描述；过长的说明多是页面抓取
#: 文本（实测有 160 字），作为描述会稀释关键特征，因此设上限。
_DESCRIPTION_FALLBACK_MAX_LENGTH = 60


def _current_node_id() -> str:
    """当前 pytest 节点 ID（用于把自愈记录挂到具体用例上）。"""

    return os.getenv("PYTEST_CURRENT_TEST", "").split(" (", 1)[0]


def _healing_evidence(result: ElementResultModel) -> dict[str, Any] | None:
    """从元素结果里提取自愈观测字段；未发生自愈时返回 ``None``。"""

    engine = getattr(result, "locator_engine", None)
    if not isinstance(engine, dict) or not engine:
        return None
    used_source = str(engine.get("used_source") or FIXED_LOCATOR_SOURCE)
    used_ai = bool(engine.get("used_ai"))
    temporary_heal_used = bool(engine.get("temporary_heal_used"))
    if not used_ai and not temporary_heal_used and used_source == FIXED_LOCATOR_SOURCE:
        return None
    trace = engine.get("trace") if isinstance(engine.get("trace"), dict) else {}
    raw_stages = trace.get("stages") if isinstance(trace.get("stages"), list) else []
    decision = trace.get("decision") if isinstance(trace.get("decision"), dict) else {}
    return {
        "used_source": used_source,
        "used_ai": used_ai,
        "temporary_heal_used": temporary_heal_used,
        "auto_apply_eligible": bool(engine.get("auto_apply_eligible")),
        "final_score": engine.get("final_score"),
        "candidate_count": engine.get("candidate_count"),
        "heal_record_id": engine.get("heal_record_id"),
        "reject_reasons": list(engine.get("reject_reasons") or [])[:10],
        "model": trace.get("model"),
        "prompt_version": trace.get("prompt_version"),
        "schema_version": trace.get("schema_version"),
        "agent_called": trace.get("agent_called"),
        "circuit_breaker": trace.get("agent_circuit_breaker"),
        "decision": decision.get("status"),
        "stages": [
            {
                "name": item.get("name"),
                "duration_ms": item.get("duration_ms"),
                "candidate_count": item.get("candidate_count"),
                "error": item.get("error"),
            }
            for item in raw_stages
            if isinstance(item, dict)
        ][:10],
    }
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
        # prompt 由 ElementDefinition 统一写入 elements[0]：库侧 first_prompt
        # 只取第一个非空 prompt，逐 slot 分开填会让第 2、3 组提示词对 AI 失效。
        return ElementListModel(exp=exp, loc=loc, sub=sub, slot=self.slot)


@dataclass(frozen=True)
class ElementDefinition:
    element_id: int
    project_name: str
    module_name: str
    page_name: str
    name: str
    locators: tuple[LocatorDefinition, ...]
    description: str | None = None
    #: 三组 AI 定位提示词按行合并后的元素级描述，运行时写入 ``elements[0].prompt``。
    prompt: str | None = None

    @property
    def is_description_only(self) -> bool:
        """是否为"只有描述、没有固定定位器"的元素。

        这类元素依赖定位引擎（元素自愈）现场找目标：库侧在 ``elements`` 为空且
        ``description_template`` 非空时会合成一个占位定位组，直接跳过固定定位阶段。
        """

        return not self.locators

    @property
    def ai_description(self) -> str | None:
        """交给 AI 的元素描述：优先提示词，其次说明列（过滤超长噪声）。"""

        if self.prompt:
            return self.prompt
        fallback = (self.description or "").strip()
        if fallback and len(fallback) <= _DESCRIPTION_FALLBACK_MAX_LENGTH:
            return fallback
        return None

    @property
    def element_version(self) -> int:
        """定位器 + 提示词配置的内容指纹。

        观测里用作 ``base_locator_version``：定位表达式或提示词变更后，
        历史自愈记录即失效。**不能用元素 ID 冒充**——ID 是稳定身份，
        配置变了它不会变。
        """

        payload = json.dumps(
            {
                "locators": [
                    [str(item.method), item.expression, item.index]
                    for item in self.locators
                ],
                "prompt": self.ai_description,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return int(hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8], 16)

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
                    # 保留逐 slot 原值，仅用于 Allure 证据展示；
                    # 真正交给 AI 的是下面按行合并后的元素级描述。
                    prompt=_optional_text(
                        _value(record, f"AI定位提示词{slot}", "AI定位提示词", "提示词")
                    ),
                    slot=slot,
                )
            )
        prompt = merge_prompt_columns(record)
        if not locators:
            # 描述即定位：元素表只填 AI 定位提示词、不填定位方式/表达式时，
            # 交由定位引擎现场定位。库侧会在 elements 为空且 description_template
            # 非空时合成占位定位组，跳过固定定位阶段直接进入自愈。
            if not prompt:
                raise ValueError(
                    f"元素 {_value(record, '元素名称', '*元素名称')} "
                    "既没有有效定位表达式，也没有 AI 定位提示词"
                )
        return cls(
            element_id=int(_value(record, "ID", "元素ID")),
            project_name=str(_value(record, "项目名称", default="")),
            module_name=str(_value(record, "模块名称", default="")),
            page_name=str(_value(record, "页面名称", default="")),
            name=str(_value(record, "元素名称", "*元素名称")),
            locators=tuple(locators),
            description=_optional_text(record.get("说明")),
            prompt=prompt,
        )

    def to_element_model(
        self,
        *,
        operation_type: ElementOperationEnum,
        method: str,
        arguments: list[MethodModel],
        locators: tuple[LocatorDefinition, ...] | None = None,
    ) -> ElementModel:
        element_models = [item.to_model() for item in (locators or self.locators)]
        description = self.ai_description
        if description and element_models:
            # 三组提示词按行合并后只写到第一组：库侧 first_prompt 只读第一个非空 prompt。
            element_models[0] = element_models[0].model_copy(
                update={"prompt": description}
            )
        return ElementModel(
            id=self.element_id,
            element_id=self.element_id,
            type=operation_type,
            name=self.name,
            # 页面键（componentsPage）对模型语义很弱，映射成中文页面名。
            category=page_display_name(self.project_name, self.page_name)
            or self.page_name
            or self.module_name,
            description_template=description,
            element_version=self.element_version,
            elements=element_models,
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
        self._check_description_only_elements()

    def _check_description_only_elements(self) -> None:
        """在构造期暴露"描述型元素但未开启自愈"的配置错误。

        这类元素没有固定定位器，唯一出路是定位引擎；若自愈被关闭，它们必然在
        执行时才失败。这里提前一次性报出全部相关元素名，避免用例跑到一半才暴露，
        也避免只看到第一个失败的元素。
        """

        if self.base_data.locator_engine is not None:
            return
        list_all = getattr(self.repository, "all", None)
        if not callable(list_all):
            return
        try:
            definitions = list_all()
        except Exception:  # 元素源本身不可用时不在构造期重复放大问题
            return
        names = [item.name for item in definitions if item.is_description_only]
        if not names:
            return
        preview = "、".join(names[:5])
        raise ValueError(
            "以下元素只有 AI 定位提示词、没有固定定位器，但元素自愈未开启："
            f"{preview}{'…' if len(names) > 5 else ''}；"
            "请设置 ELEMENT_HEALING_ENABLED=true，或为这些元素补充固定定位方式/表达式"
        )

    def _configure_healing(self, settings) -> None:
        """装配元素自愈引擎，并把降级原因显式写进日志。

        ``standalone()`` 在 ``api_key`` 为空时不会创建模型客户端，AI 会**静默关闭**；
        这里把"未启用 / 启用了但缺凭据 / 已启用"三种状态区分开，避免线上排查时
        只能看到"AI 没生效"却不知道原因。
        """

        log = self.base_data.log
        enabled = bool(getattr(settings, "ELEMENT_HEALING_ENABLED", True))
        if not enabled:
            log.info("[AI 定位] 未启用：ELEMENT_HEALING_ENABLED=false，固定定位失败后不会自愈")
            return
        if self.base_data.locator_engine is not None:
            log.debug("[AI 定位] 复用已装配的定位引擎，跳过重复初始化")
            return
        ai_enabled = bool(getattr(settings, "AI_ELEMENT_HEALING_ENABLED", False))
        api_key = str(getattr(settings, "AI_API_KEY", "") or os.getenv("MANGO_AI_API_KEY", ""))
        model = str(getattr(settings, "AI_MODEL", "THUDM/GLM-Z1-9B-0414"))
        if ai_enabled and not api_key:
            log.warning(
                "[AI 定位] 已请求启用但缺少凭据：AI_ELEMENT_HEALING_ENABLED=true 而 "
                "AI_API_KEY 为空（该值只允许由环境变量或 CI Secret 注入），"
                "本次运行只会执行本地自愈，不会调用模型"
            )
        elif not ai_enabled:
            log.info("[AI 定位] 未启用：AI_ELEMENT_HEALING_ENABLED=false，只执行本地自愈")
        else:
            log.info(f"[AI 定位] 已启用：模型={model}，固定定位重试窗口耗尽后触发")
        engine = WebElementHealingHarness.standalone(
            # 缺凭据时显式传 None：standalone 只要 api_key 为空就不会创建模型客户端，
            # 这里传 None 而不是空串，让"降级为本地自愈"的意图在调用处就可见。
            api_key=(api_key or None) if ai_enabled else None,
            base_url=str(getattr(settings, "AI_BASE_URL", "https://api.siliconflow.cn/v1")),
            model=model,
            timeout=int(getattr(settings, "AI_TIMEOUT", 30)),
            mode=int(getattr(settings, "ELEMENT_HEALING_MODE", 2)),
            semantic_strength=int(getattr(settings, "AI_SEMANTIC_STRENGTH", 0)),
            logger=self.base_data.log,
        )
        self.base_data.set_locator_engine(engine)
        self.base_data.is_ai = bool(ai_enabled and api_key)

    def _require_healing_engine(self, definition: ElementDefinition) -> None:
        """描述型元素没有固定定位器，必须依赖定位引擎才能执行。"""

        if not definition.is_description_only:
            return
        if self.base_data.locator_engine is not None:
            return
        raise ValueError(
            f"元素 {definition.name} 只有 AI 定位提示词、没有固定定位器，"
            "需要开启元素自愈（ELEMENT_HEALING_ENABLED=true）才能执行"
        )

    def _record_healing_result(
        self, definition: ElementDefinition, result: ElementResultModel
    ) -> None:
        """把自愈结果提升为独立的 Allure 步骤与运行级统计。

        未发生自愈（固定定位一次命中）时不产生任何附加信息，避免给绝大多数
        正常用例增加噪声。
        """

        evidence = _healing_evidence(result)
        if not evidence:
            return
        attach_json("AI 自愈", evidence)
        try:
            allure.dynamic.label("healed", "true")
            allure.dynamic.label("heal_source", str(evidence["used_source"]))
            allure.dynamic.label(
                "heal_mode", "ai" if evidence["used_ai"] else "local"
            )
            if evidence.get("model"):
                allure.dynamic.label("heal_model", str(evidence["model"]))
        except Exception:  # 无 Allure 生命周期时（如单测）忽略标签
            pass
        healing_metrics.record(HealingEvent(
            element_name=definition.name,
            case_id=_current_node_id(),
            used_source=str(evidence["used_source"]),
            used_ai=bool(evidence["used_ai"]),
            temporary_heal_used=bool(evidence["temporary_heal_used"]),
            final_score=evidence.get("final_score"),
            model=evidence.get("model"),
            prompt_version=evidence.get("prompt_version"),
            operation_failed=result.status != StatusEnum.SUCCESS.value,
        ))

    def locator(self, name: str) -> Locator:
        """Resolve a Locator via mangoautomation for compatibility-only page reads."""
        definition = self.repository.get(name)
        if definition.is_description_only:
            raise ValueError(
                f"元素 {definition.name} 是描述型元素（只有 AI 定位提示词），"
                "不支持直接读取 Locator；请改用 execute() 走元素自愈"
            )
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
        self._require_healing_engine(definition)
        all_definitions = (definition, *(self.repository.get(item) for item in target_names))
        for item in all_definitions:
            self._require_healing_engine(item)
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
                self._record_healing_result(definition, result)
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
