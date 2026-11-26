"""元素读取使用临时工作簿和临时产品注册，不依赖维护中的业务资产。"""

import pytest
from openpyxl import Workbook

from core.sources.element_schema import CANONICAL_ELEMENT_HEADERS
import core.sources.page_labels as labels
import core.sources.ui_elements as sources
from core.ui.element_repository import source_element_repository
from .records import element_record


@pytest.fixture(autouse=True)
def isolated_element_sources(monkeypatch):
    sources.load_ui_element_records.cache_clear()
    source_element_repository.cache_clear()
    monkeypatch.setattr(labels, "PRODUCT_PAGE_LABELS", {
        "框架测试产品": {"formPage": "表单页"},
    })
    try:
        yield
    finally:
        sources.load_ui_element_records.cache_clear()
        source_element_repository.cache_clear()


@pytest.fixture
def element_workbook(tmp_path_factory, monkeypatch):
    directory = tmp_path_factory.mktemp("element-source")
    monkeypatch.setattr(sources, "WORKBOOK_DIR", directory)
    monkeypatch.setattr(sources, "PRODUCT_WORKBOOKS", {"sample_ui": ("elements.xlsx",)})
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "UI元素"
    sheet.append(CANONICAL_ELEMENT_HEADERS)
    records = [
        element_record(),
        element_record(ID=8, 元素名称="cancel-button", 定位表达式1="cancel-button"),
        element_record(ID=9, 元素名称="search-button", 模块名称="search", 页面名称="searchPage"),
    ]
    for record in records:
        sheet.append([record.get(column) for column in CANONICAL_ELEMENT_HEADERS])
    workbook.save(directory / "elements.xlsx")
    workbook.close()
    return directory
