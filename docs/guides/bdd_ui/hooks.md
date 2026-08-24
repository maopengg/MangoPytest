# Hooks — 统一生命周期说明

`bdd_ui` 不再维护项目级 hooks 目录。

- 浏览器启动、Context/Page 创建和关闭：`core/ui/pytest_support.py`
- 截图、页面 HTML、控制台日志和 Trace：`core/ui/artifacts.py`
- Allure 请求、响应、UI 步骤和 Fixture 证据：`core/execution/pytest_evidence_plugin.py`
- Mango Mock Test Run 清理：`MangoMockRepositories.close()`

新增项目时应复用这些公共入口，只在项目 Fixture 中装配本项目对象。
