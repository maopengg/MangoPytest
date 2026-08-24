# Repository — BDD API 领域访问

Repository 按业务域拆分在 `repos/`：

- `cross_protocol/`：组合 HTTP、WebSocket、SSE、MCP、gRPC 客户端并管理 Test Run。
- `functional_cases/`：认证、订单、报销、评审、故障等功能接口。
- `products/`：商品领域访问。

Steps 和测试绑定禁止直接访问协议客户端私有字段；测试数据创建与清理必须通过 Factory/Repository 完成。
