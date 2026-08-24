# Config — BDD API 配置

`BddApiMockConfig` 继承 `core.api.APIRuntimeConfig`。配置加载只解析字段，不创建数据库 Engine 或网络连接。

环境文件通过 `Path(__file__).parent / ".env.<name>"` 加载；可执行环境以 `auto_tests/project_registry.py` 为准，当前只开放 `test`。Web 控制台允许临时覆盖注册的 `BASE_URL` 和 `MOCK_TIMEOUT`，覆盖只作用于当前测试子进程。
