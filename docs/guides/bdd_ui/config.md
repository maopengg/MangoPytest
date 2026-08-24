# Config — UI 运行配置

项目配置继承 `core.ui.UIRuntimeConfig`，只声明项目名称、产物目录和环境差异，不初始化数据库或浏览器。

```python
class BddUIMockConfig(UIRuntimeConfig):
    ELEMENT_PROJECT = "mock_ui"
    ELEMENT_PRODUCT = "MockUI服务"
    ARTIFACT_DIR = artifact_path("reports", "bdd_ui", "artifacts")
```

环境文件使用 `Path(__file__).parent / ".env.<name>"` 加载。可执行环境以 `auto_tests/project_registry.py` 为唯一来源；当前 `bdd_ui` 只注册了 `test`，所以 Web 控制台和 `main.py` 都只允许选择 `test`。

执行页面可临时覆盖注册表中明确声明的运行参数，例如浏览器类型、无头模式、元素来源和元素自愈选项。临时覆盖只进入当前子进程，不修改配置文件。
