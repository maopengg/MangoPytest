# Conftest — BDD API 装配

`conftest.py` 显式注册项目 Steps，并提供场景上下文、跨协议 Repository、领域 Factory 和执行器 Fixture。

每个 `CrossProtocolRepository` 在 Fixture 开始时创建隔离 Test Run，在结束时关闭协议客户端并清理 Test Run。项目不使用会话级数据库清理 hooks。
