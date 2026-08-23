# UI Mock 元素仓库

本目录是 `simple_ui` 项目唯一的元素定义入口，只读取本地 Excel，不使用飞书。

- `ui_elements.xlsx`：本地元素仓库，包含 260 个新版 `data-testid` 元素。
- `repository.py`：统一查询入口，只读取工作簿中的 `UI元素` 工作表。

测试代码不直接拼接 CSS 或调用 `page.get_by_test_id()`，统一使用：

```python
from auto_tests.ui.simple_ui.elements import elements

locator = elements.locate(page, "single-click-target")
```

工作簿字段为：`ID`、`项目名称`、`模块名称`、`页面名称`、`元素名称`、
`定位方式1`、`表达式1`、`下标1` 等。新版元素使用 `TEST_ID`，也兼容
`CSS`、`XPATH`、`TEXT` 和 `PLACEHOLDER`。
