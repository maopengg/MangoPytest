# pytest_api

面向测试开发和研发团队的纯 pytest 多协议 API 自动化 Demo，共 165 条用例。
项目直接连接远程 Mango Mock，覆盖 HTTP、Webhook、SSE、WebSocket、MCP、gRPC
以及跨协议业务一致性。

## 五层架构

```text
L5 test_cases/       pytest 测试、marks、参数化与 DAL 断言
 ↓
L4 services/         业务 Service 与跨协议 Workflow
 ↓
L3 data_factory/     entities、specs、factories
 ↓
L2 repositories/    按业务域封装原子访问和自动清理
 ↓
L1 ../common/mango_mock/  公共 HTTP/WS/SSE/MCP/gRPC 客户端
```

本项目不包含 Feature、Steps 或 `pytest_bdd` 绑定，也不使用按 Case ID 区间分发
的集中执行器。测试函数只调用 Fixture、Factory、Repository 或 Service 的公开方法。

## 目录职责

- `test_cases/`：165 条纯 pytest 用例，保留 FTAPI Case ID 和 Allure 元数据。
- `services/`：按业务域或协议拆分的可复用场景编排。
- `data_factory/`：强类型实体、合法/边界数据规格和唯一数据生成。
- `repositories/`：接口路径、认证、协议细节与 Test Run 生命周期。
- `fixtures/`：function scope 隔离运行、Repository、Factory 和 Service 注入。

## 执行

必须使用项目 `.venv` 并显式指定环境：

```bash
ENV=test .venv/bin/python -m pytest auto_tests/api/pytest_api/test_cases

# 并行执行（Test Run 按 function scope 隔离）
ENV=test .venv/bin/python -m pytest auto_tests/api/pytest_api/test_cases -n 4
```

`test` 环境使用 `http://43.142.161.61:8003`，不依赖本地 `mango-mock`。
内部包只允许从项目 `local_packages/` 安装，禁止使用 PyPI 旧版本。
