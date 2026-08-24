# pytest_api — 大型纯 pytest API Demo

`pytest_api` 使用纯 pytest、参数化、Fixture 和 Allure 元数据表达 165 条 Mango Mock API 用例，不依赖 Feature 或 pytest-bdd。

## 五层调用链

```text
Tests
  → Services / Workflows
  → Data Factory（entities/factories/specs）
  → Repositories
  → auto_tests/common/mango_mock 协议客户端
```

## 当前结构

```text
auto_tests/api/pytest_api/
├── test_cases/       # 按 auth/orders/claims/协议域拆分测试
├── services/         # 业务场景与跨协议编排
├── data_factory/     # 强类型数据模型和数据工厂
├── repositories/    # 领域数据访问与自动清理
├── fixtures/        # 项目级对象装配
├── config/          # API 运行配置
└── conftest.py
```

HTTP、WebSocket、SSE、MCP 和 gRPC 客户端统一位于 `auto_tests/common/mango_mock/`。测试函数只能调用 Factory、Repository 或 Service 公开方法，不直接访问协议客户端私有字段。

## 运行

```bash
ENV=test .venv/bin/python main.py --project pytest_api
ENV=test .venv/bin/python main.py --project pytest_api --collect-only -- -q
```

可执行环境由 `auto_tests/project_registry.py` 声明；当前只开放 `test`。
