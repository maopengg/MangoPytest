# Fixtures — BDD API 资源生命周期

主要 Fixture 包括：

- `scenario_context`：步骤间传递结构化响应和业务状态。
- `cross_protocol_repository`：主隔离 Test Run 与协议客户端。
- `secondary_repository`：跨 Test Run 隔离场景。
- `cross_protocol_factory`、领域 Factory：创建强类型前置数据。
- `api_response`：向通用 DAL 断言步骤暴露当前响应。

所有持有连接或 Test Run 的 Fixture 必须使用 `yield` 并在结束阶段调用 `close()`。
