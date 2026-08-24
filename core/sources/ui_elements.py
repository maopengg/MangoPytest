"""按项目产品加载 Excel 或飞书 UI 元素。"""

from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from core.sources.element_schema import REQUIRED_ELEMENT_HEADERS
from core.sources.excel import ExcelWorkbookSource
from core.sources.feishu.document_data import DocumentData


class ElementSourceType(str, Enum):
    EXCEL = "excel"
    FEISHU = "feishu"


WORKBOOK_DIR = Path(__file__).with_name("workbooks") / "mock_ui"
PRODUCT_WORKBOOKS = {
    "mock_ui": ("mock_ui_elements.xlsx",),
}


@lru_cache(maxsize=12)
def load_ui_element_records(
    *,
    source: str,
    project: str,
    product_name: str,
) -> tuple[dict[str, Any], ...]:
    """加载一个 UI Demo 的元素记录。

    ``source`` 只接受 ``excel`` 或 ``feishu``；``project`` 用于选择本地产品
    工作簿，``product_name`` 对飞书记录按“项目名称”过滤。
    """

    try:
        source_type = ElementSourceType(str(source).strip().lower())
    except ValueError as exc:
        raise ValueError(f"不支持的 UI 元素来源：{source}") from exc
    if project not in PRODUCT_WORKBOOKS:
        raise ValueError(f"未注册 UI 元素产品：{project}")
    if source_type is ElementSourceType.EXCEL:
        records = tuple(
            record
            for file_name in PRODUCT_WORKBOOKS[project]
            for record in ExcelWorkbookSource(WORKBOOK_DIR / file_name).records(
                "UI元素",
                required_headers=REQUIRED_ELEMENT_HEADERS,
            )
        )
    else:
        frame = DocumentData().ui_element()
        records = tuple(
            record
            for record in frame.to_dict(orient="records")
            if str(record.get("项目名称", "")).strip() == product_name
        )
    _validate_element_records(records, project, product_name)
    return records


def _validate_element_records(
    records: tuple[dict[str, Any], ...],
    project: str,
    product_name: str,
) -> None:
    if not records:
        raise ValueError(f"{project} UI 元素数据不能为空")
    names = [str(record["元素名称"]).strip() for record in records]
    ids = [int(record["ID"]) for record in records]
    products = {str(record["项目名称"]).strip() for record in records}
    if products != {product_name}:
        raise ValueError(
            f"{project} UI 元素产品不匹配：期望 {product_name}，实际 {sorted(products)}"
        )
    if len(names) != len(set(names)):
        raise ValueError(f"{project} UI 元素存在重复元素名称")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{project} UI 元素存在重复元素 ID")
