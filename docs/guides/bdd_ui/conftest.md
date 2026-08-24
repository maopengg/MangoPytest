# Conftest — BDD UI 注册入口

`conftest.py` 只注册当前项目明确需要的 Fixture 与 Steps：

```python
pytest_plugins = [
    "auto_tests.ui.bdd_ui.fixtures.bdd",
    "auto_tests.ui.bdd_ui.steps.mango_mock_steps",
    "auto_tests.ui.bdd_ui.steps.business_steps",
]
```

能力矩阵的优先级在 `pytest_collection_modifyitems` 中转换为 `p0/p1/p2` 标记。浏览器生命周期、失败截图、HTML、控制台日志和 Trace 由 `core.ui` 与根 pytest 插件统一处理，项目不再维护独立 hooks。
