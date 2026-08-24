# Repository — Mango Mock 产品数据访问

UI 项目统一使用：

```text
auto_tests/common/mango_mock/repositories/
├── context.py     # Test Run、认证与清理上下文
├── domains.py     # 订单、报销、评审等领域 Repository
└── bundle.py      # MangoMockRepositories 聚合入口
```

Repository 只访问公共 Mango Mock 协议客户端。BDD 和纯 pytest 项目的数据工厂分别调用相同领域 Repository，避免复制 HTTP 请求和清理逻辑。

Fixture 必须在结束时调用 `repositories.close()`；清理由隔离 Test Run 的 cleanup token 完成，不使用项目级数据库清理 hooks。
