# Hooks — 当前清理机制

`bdd_api` 不维护独立 hooks 目录。清理由 Fixture 和 Repository 生命周期完成：

```text
Fixture 创建 Repository → Repository.start() 创建 Test Run
测试执行 → Repository.close() 关闭协议连接并清理 Test Run
```

请求、响应、日志和 Fixture 阶段证据由根 pytest 插件 `core.execution.pytest_evidence_plugin` 统一采集。
