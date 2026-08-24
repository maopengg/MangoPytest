# Page Object — Mango Mock 产品公共页面

BDD UI 与纯 pytest UI 测试同一个 Mango Mock 产品，因此 Page Object 与 Flow 位于：

```text
auto_tests/common/mango_mock/ui_business/
├── pages.py
└── flows.py
```

页面对象通过 `configured_element_repository(settings)` 和 `element_runtime(...)` 获取 `ElementModel`，调用 `element_action()` 执行 mangoautomation 操作。Tests、Steps 和 Flow 不直接操作 Playwright Locator。

项目 Fixture 负责注入 `base_data` 与项目 `settings`：

```python
OrderFlow(OrderPage(base_data, settings))
```

元素工作簿统一位于 `core/sources/workbooks/mock_ui/mock_ui_elements.xlsx`，BDD/pytest/simple 三个 Demo 不复制元素文件。
