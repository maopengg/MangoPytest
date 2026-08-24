# bdd_api — 大型 BDD API Demo

`bdd_api` 使用中文 Gherkin 表达 165 条 Mango Mock API 功能用例，覆盖 HTTP、WebSocket、SSE、MCP、gRPC、Webhook 和故障实验。

```text
Feature → Steps → Data Factory → Repository
        → auto_tests/common/mango_mock 公共协议客户端
```

项目目录保留 `features/steps/data_factory/repos/test_cases`，与纯 pytest API 的 `tests/services/data_factory/repositories` 形成两种可选的大项目组织方式。Case 与数据工厂有意独立，底层协议请求统一共享。
