# simple_api

面向初学者和小型项目的轻量纯 pytest API Demo，共 16 条独立用例。它展示最少必要分层：

```text
Tests → Fixture → Factory + Repository → common/mango_mock HTTP Client
```

- Tests 只调用 Repository 的公开方法并完成断言。
- Factory 生成 `AUTO_` 前缀的隔离数据。
- Repository 创建 Test Run，并在 fixture 结束时自动清理。
- 不使用 Gherkin、Steps、集中执行器或私有协议字段。

运行：

```bash
ENV=test .venv/bin/python main.py --project simple_api
ENV=test .venv/bin/python -m pytest auto_tests/api/simple_api
```

Mango Mock 默认测试地址为 `http://43.142.161.61:8003`。

项目结构：

```text
simple_api/
├── config/
├── data_factory/
│   ├── entities/
│   ├── factories/
│   └── specs/
├── fixtures/
├── repositories/simple_api/
├── test_cases/simple_api/
├── conftest.py
└── pytest.ini
```

三个 API Demo 的定位：

| 项目 | 方式 | 适用范围 |
|---|---|---|
| `simple_api` | 轻量纯 pytest | 入门、小型项目、少量接口 |
| `bdd_api` | 中文 Gherkin BDD | 业务共同评审与验收场景 |
| `pytest_api` | 五层纯 pytest | 大项目、多业务域与多协议编排 |
