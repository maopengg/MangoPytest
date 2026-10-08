"""元素表 AI 定位提示词的数据契约：三列合并规则与填写体检。

元素表固定 18 列（``AGENTS.md``），其中三组 ``AI定位提示词`` 列的语义被约定为
**同一段描述的三行**：

| 列 | 语义 |
|---|---|
| ``AI定位提示词1`` | 控件描述（控件种类 + 区分特征），必填 |
| ``AI定位提示词2`` | 所在区域 / 上下文，可选 |
| ``AI定位提示词3`` | 排除项，**必须以 ``排除项：`` 开头**，可选 |

之所以要合并：mangoautomation 只读取 ``ElementListModel`` 列表中**第一个非空**
``prompt``（``element_healing/context/sanitizer.py`` 的 ``first_prompt``），
不合并的话第 2、3 列对 AI 完全无效。

之所以必须用换行而不是 ``|`` 之类的分隔符：库侧 ``positive_prompt`` 按**行首**
匹配剔除 ``排除项：``；一旦它不是独立行的行首，就会被当成**正向必需文本**，
语义完全反转（见 ``lint_records`` 的 ``exclusion_not_at_line_start`` 规则）。
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Collection, Iterable, Mapping

#: 参与 AI 描述的三列（顺序即合并后的行序）。
PROMPT_COLUMNS = ("AI定位提示词1", "AI定位提示词2", "AI定位提示词3")

#: 单列为空时的兼容别名（与 ``ElementDefinition.from_record`` 的取值顺序一致）。
PROMPT_ALIASES = ("AI定位提示词", "提示词")

#: 排除项必须以它为行首（与库侧 ``positive_prompt`` 的匹配规则保持一致）。
_EXCLUSION_LINE = re.compile(r"^\s*排除项\s*[：:]")
_EXCLUSION_MENTION = re.compile(r"排除项")
_VARIABLE = re.compile(r"\$\{\{([^{}]*)\}\}")
_TEMPLATE = re.compile(r"^\s*查找元素\s*[：:]")
_NAME_SEPARATOR = re.compile(r"[-_/|｜>：:\s]+")

MIN_PROMPT_LENGTH = 6
MAX_PROMPT_LENGTH = 120

#: 只有交互类元素才需要写"控件种类"——库侧 target_intent 用它来拒绝种类不符的候选，
#: 对纯展示元素没有约束意义。这里用元素名做近似判断，避免对
#: history-result / demo-table / read-text-target 这类展示元素持续产生不可执行的告警。
_INTERACTIVE_NAME_HINTS = (
    "input", "button", "btn", "select", "link", "click", "hover", "tap",
    "dblclick", "upload", "download", "check", "toggle", "switch", "topic",
    "copy", "connect", "disconnect", "send", "ping", "subscribe",
    "unsubscribe", "query", "approve", "poll", "validate", "open-", "show-",
    "start-", "stop", "cancel", "reset", "load-", "create", "pay-", "refund",
    "seed", "clear", "read-", "drag", "drop", "sort", "filter", "refresh",
    "capture", "apply", "restore", "trigger", "login", "cleanup", "-name",
    "-key", "delay", "repeat", "interval", "quantity", "amount", "-password",
)

#: 命中这些后缀的元素按"展示/容器"处理，不参与控件种类建议。
_DISPLAY_NAME_SUFFIXES = (
    "-result", "-log", "-status", "-summary", "-count", "-total", "-no", "-id",
    "-stage", "-description", "-version", "-messages", "-types", "-example",
    "-reference", "-catalog", "-timeline", "-manifest", "-fingerprint",
    "-locator", "-panel", "-page", "-form", "-table", "-list", "-tree",
    "-zone", "-host", "-region", "-slot", "-pad", "-marker", "-content",
    "-header", "-lockup", "-navigation", "-toast", "-modal", "-target",
    "-child", "-source", "-duration", "-loading", "-progress",
)

ERROR = "error"
WARNING = "warning"


def _looks_interactive(element_name: str) -> bool:
    lowered = str(element_name).lower()
    if lowered.endswith(_DISPLAY_NAME_SUFFIXES):
        return False
    return any(hint in lowered for hint in _INTERACTIVE_NAME_HINTS)


def _clean_column(value: Any) -> str | None:
    """把一列单元格规范化为若干非空行。"""

    if value is None:
        return None
    lines = [line.strip() for line in str(value).splitlines()]
    text = "\n".join(line for line in lines if line)
    return text or None


def merge_prompt_columns(record: Mapping[str, Any]) -> str | None:
    """按列序合并三组提示词列，返回交给 AI 的多行描述。

    返回 ``None`` 表示该元素没有任何提示词——此时 AI 只能拿到元素名。
    """

    parts: list[str] = []
    for index, column in enumerate(PROMPT_COLUMNS):
        value = record.get(column)
        if index == 0 and not _clean_column(value):
            for alias in PROMPT_ALIASES:
                value = record.get(alias)
                if _clean_column(value):
                    break
        cleaned = _clean_column(value)
        if cleaned:
            parts.append(cleaned)
    return "\n".join(parts) if parts else None


def positive_prompt_lines(prompt: str | None) -> list[str]:
    """返回剔除排除项后的正向描述行，与库侧 ``positive_prompt`` 语义一致。"""

    if not prompt:
        return []
    return [
        line.strip()
        for line in str(prompt).splitlines()
        if line.strip() and not _EXCLUSION_LINE.match(line)
    ]


@dataclass(frozen=True, slots=True)
class PromptIssue:
    """一条体检结论。"""

    level: str
    rule: str
    element_id: Any
    element_name: str
    detail: str

    @property
    def is_error(self) -> bool:
        return self.level == ERROR

    def describe(self) -> str:
        return f"[{self.level}] {self.rule} 元素《{self.element_name}》{self.detail}"


def _control_and_scope_aliases() -> tuple[str, ...]:
    """复用内部包的关键词表；取不到时退回最小集合，避免体检随版本失效。"""

    try:  # pragma: no cover - 依赖内部包结构
        from mangoautomation.element_healing.verification.target_intent import (
            CONTROL_KINDS,
            SCOPE_KINDS,
        )

        aliases: list[str] = []
        for kind in CONTROL_KINDS:
            aliases.extend(kind.aliases)
        for _, scope_aliases in SCOPE_KINDS:
            aliases.extend(scope_aliases)
        return tuple(dict.fromkeys(aliases))
    except Exception:  # pragma: no cover - 内部包结构变化时的兜底
        return (
            "文件上传", "上传控件", "选择文件", "单选框", "单选按钮", "复选框", "勾选框",
            "多选框", "开关", "下拉框", "选择框", "输入框", "文本框", "按钮", "链接",
            "卡片", "表格行", "列表项", "弹窗", "对话框", "抽屉", "表单",
        )


CONTROL_AND_SCOPE_ALIASES = _control_and_scope_aliases()


def _variables(prompt: str) -> list[str]:
    """提取 ``${{var}}`` 中的变量名（兼容 ``${{key|alias}}`` 写法）。"""

    return [
        match.group(1).split("|", 1)[0].strip()
        for match in _VARIABLE.finditer(prompt)
    ]


def lint_prompt(
    *,
    element_id: Any,
    element_name: str,
    columns: Iterable[Any],
    has_locator: bool,
    allowed_variables: Collection[str] = (),
) -> list[PromptIssue]:
    """对单个元素的提示词列做体检。"""

    issues: list[PromptIssue] = []
    record = {column: value for column, value in zip(PROMPT_COLUMNS, columns)}

    # 逐行检查排除项位置：不在行首会导致语义反转，必须报错。
    for column, value in record.items():
        cleaned = _clean_column(value)
        if not cleaned:
            continue
        for line in cleaned.splitlines():
            if _EXCLUSION_MENTION.search(line) and not _EXCLUSION_LINE.match(line):
                issues.append(PromptIssue(
                    ERROR, "exclusion_not_at_line_start", element_id, element_name,
                    f"的 {column} 中「排除项」未独占行首：{line!r}；"
                    "库侧按行首匹配剔除排除条件，写在句中会被当成必须命中的目标文本",
                ))

    merged = merge_prompt_columns(record)
    if not merged:
        if has_locator:
            issues.append(PromptIssue(
                WARNING, "missing_prompt", element_id, element_name,
                "没有任何 AI 定位提示词，固定定位失效时 AI 只能依据元素名推断",
            ))
        return issues

    positive_lines = positive_prompt_lines(merged)
    if not positive_lines:
        issues.append(PromptIssue(
            ERROR, "exclusion_only", element_id, element_name,
            "只填了排除项、没有任何正向描述，AI 无法知道要找什么",
        ))

    if _TEMPLATE.match(merged.strip()):
        issues.append(PromptIssue(
            WARNING, "template_prompt", element_id, element_name,
            "仍是「查找元素：<元素名>」模板串，与元素名等价、无增量语义",
        ))

    normalized_name = _NAME_SEPARATOR.sub("", str(element_name)).lower()
    normalized_prompt = _NAME_SEPARATOR.sub(
        "", _TEMPLATE.sub("", merged.strip()).lower()
    )
    if normalized_prompt and normalized_prompt == normalized_name:
        issues.append(PromptIssue(
            WARNING, "prompt_equals_element_name", element_id, element_name,
            "去掉模板前缀后与元素名完全相同，没有提供区分特征",
        ))

    positive_length = len("".join(positive_lines))
    if positive_lines and positive_length < MIN_PROMPT_LENGTH:
        issues.append(PromptIssue(
            WARNING, "prompt_too_short", element_id, element_name,
            f"正向描述仅 {positive_length} 个字符，建议补充控件种类与区分特征",
        ))
    elif positive_length > MAX_PROMPT_LENGTH:
        issues.append(PromptIssue(
            WARNING, "prompt_too_long", element_id, element_name,
            f"正向描述 {positive_length} 个字符，过长会稀释关键特征",
        ))

    if (
        positive_lines
        and _looks_interactive(element_name)
        and not any(alias in merged for alias in CONTROL_AND_SCOPE_ALIASES)
    ):
        issues.append(PromptIssue(
            WARNING, "missing_control_keyword", element_id, element_name,
            "未包含可识别的控件种类/作用域关键词（如 输入框、按钮、弹窗、表格行），"
            "补充后 AI 与语义校验的命中率更高",
        ))

    for name in _variables(merged):
        if name and name not in allowed_variables:
            issues.append(PromptIssue(
                ERROR, "undefined_prompt_variable", element_id, element_name,
                f"使用了运行时变量 ${{{{{name}}}}}，但未在允许列表内声明；"
                "变量未注入时 mangotools 会抛错，元素初始化直接失败（与 AI 开关无关）",
            ))

    return issues


def lint_records(
    records: Iterable[Mapping[str, Any]],
    *,
    allowed_variables: Collection[str] = (),
) -> tuple[PromptIssue, ...]:
    """对整张元素表做提示词体检。"""

    issues: list[PromptIssue] = []
    for record in records:
        columns = [record.get(column) for column in PROMPT_COLUMNS]
        if not any(_clean_column(value) for value in columns):
            # 兼容走别名的旧数据（飞书 16 列表）。
            columns[0] = next(
                (record.get(alias) for alias in PROMPT_ALIASES if _clean_column(record.get(alias))),
                None,
            )
        has_locator = bool(
            str(record.get("定位方式1") or "").strip()
            and str(record.get("定位表达式1") or "").strip()
        )
        issues.extend(lint_prompt(
            element_id=record.get("ID"),
            element_name=str(record.get("元素名称") or ""),
            columns=columns,
            has_locator=has_locator,
            allowed_variables=allowed_variables,
        ))
    return tuple(issues)


def summarize(issues: Iterable[PromptIssue]) -> dict[str, int]:
    """统计体检结论，便于日志与报告输出。"""

    counts = {ERROR: 0, WARNING: 0}
    for issue in issues:
        counts[issue.level] = counts.get(issue.level, 0) + 1
    return counts


__all__ = [
    "CONTROL_AND_SCOPE_ALIASES",
    "ERROR",
    "MAX_PROMPT_LENGTH",
    "MIN_PROMPT_LENGTH",
    "PROMPT_ALIASES",
    "PROMPT_COLUMNS",
    "WARNING",
    "PromptIssue",
    "lint_prompt",
    "lint_records",
    "merge_prompt_columns",
    "positive_prompt_lines",
    "summarize",
]
