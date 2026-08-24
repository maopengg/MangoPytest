# Data Factory — BDD UI 测试数据

BDD UI 保留独立的 `entities/factories/specs`，用于演示 BDD 项目的数据工厂组织方式。工厂不直接连接数据库，而是通过公共 `MangoMockRepositories` 创建隔离 Test Run 中的数据。

```text
BDD Step → BddUIDataFactory → Domain Factory
         → MangoMockRepositories → Mango Mock API
```

每个测试使用独立 Test Run，数据名称使用 `AUTO_BDD_UI` 前缀；Fixture 结束时由 Repository 使用 cleanup token 清理。浏览器需要的 run ID、用户、Token 和业务实体 ID 通过 `bind_browser()` 写入当前 Context 的 localStorage。

数据工厂与纯 pytest UI 有意分别保留，用户可以对比两种项目模式；底层 Repository 是产品公共代码，不允许复制。
