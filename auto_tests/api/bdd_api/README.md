# bdd_api

基于 `pytest-bdd` 的 Mango Mock 多协议功能自动化项目，目标地址由
`config/.env.*` 管理。当前用例覆盖 HTTP、Webhook、SSE、WebSocket、MCP、
gRPC 以及跨协议业务链路。

## 五层结构

```text
L5 features/                    中文 Gherkin 功能场景
L4 steps/                       common/api/auth/data/assertions 步骤
L3 data_factory/                entities/factories/specs 测试数据
L2 repos/                       按业务域封装操作与清理
L1 ../common/mango_mock/        共用 HTTP/SSE/WebSocket/MCP/gRPC 客户端
```

`test_cases/` 只负责绑定 Feature 和 pytest 标记；业务操作由 Steps 调用
Repository，Steps 不得直接访问协议客户端及其私有属性。测试数据名称统一以
`AUTO_` 开头，Test Run 由 Repository 创建并在 fixture 结束时清理。

## 目录

```text
bdd_api/
├── config/                     环境配置
├── data_factory/
│   ├── entities/               场景数据及执行结果
│   ├── factories/              测试数据构造
│   └── specs/                  声明式数据规格
├── features/                   165 条中文 Gherkin 场景
├── repos/
│   ├── cross_protocol/         跨协议业务链路
│   └── functional_cases/       功能场景操作封装
├── steps/
│   ├── api/handlers/           按协议拆分的场景处理器
│   ├── assertions/             DAL 断言
│   ├── auth/                   认证步骤
│   ├── common/                 场景上下文
│   └── data/                   Factory 数据步骤
└── test_cases/                 Feature 绑定与 pytest 标记
```

本项目的 Feature、数据工厂和 Repository 是 BDD 演示的一部分，允许与另外两个
API Demo 表达相同业务场景；仅无关业务风格的协议通信复用
`auto_tests/common/mango_mock/`。

## 执行

必须使用项目 `.venv` 并显式设置环境：

```bash
ENV=test .venv/bin/python -m pytest auto_tests/api/bdd_api -q -ra
```

`test` 环境当前指向 `http://43.142.161.61:8003/`；gRPC 使用同主机的
`50051` 端口。内部包仅从项目 `local_packages/` 安装，不使用 PyPI 旧版本。
