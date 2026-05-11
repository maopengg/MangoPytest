# BDD API 模式 — 架构总览

## 定位

使用 pytest-bdd + Gherkin 中文语法编写接口自动化测试，通过五层架构隔离职责。

## 项目结构

```
auto_tests/<project>/
├── conftest.py          → conftest.md       # pytest 入口，自动发现 + 清理钩子
├── pytest.ini           → conftest.md       # markers 定义
│
├── test_cases/          → test_cases.md     # Feature 文件 + BDD 绑定
├── steps/               → steps.md          # @given / @when / @then
├── fixtures/            → fixtures.md       # pytest fixtures
├── config/              → config.md         # 多环境配置
├── data_factory/        → data_factory.md   # Entity + Spec 数据工厂
├── repos/               → repos.md          # Repository 数据访问 + 清理
├── hooks/               → hooks.md          # 会话级数据清理
└── api_client.py        → api_client.md     # BDD 兼容 API 客户端
```

## 五层架构

```
L5: test_cases/          Feature 文件（中文 Gherkin）+ BDD 绑定脚本
        │
L4: steps/ + fixtures/   步骤定义 + pytest fixtures
        │
L3: data_factory/        SQLAlchemy Entity + factory_boy Spec
        │
L2: repos/               Repository（CRUD + 级联清理）
        │
L1: 数据库 + 外部 API
```

## 数据流

```
Feature 文件: 假如 存在"用户"
    ↓
步骤定义: create_entity_step("用户")
    ↓
数据工厂: UserSpec() → factory_boy → INSERT INTO users
    ↓
清理系统: pytest_sessionstart → UserRepo.delete_by_pattern("AUTO_%")
    ↓
    cascade → 删 orders → 删 reimbursements → 删 approvals → 删 logs
```

## 关键设计

| 设计点 | 文档 | 核心思路 |
|--------|------|---------|
| 环境切换 | config.md | Pydantic Settings + `.env.{env}` 文件 |
| 步骤发现 | conftest.md | `_discover_modules()` 自动扫 `steps/` |
| 数据创建 | data_factory.md | factory_boy `@register` → pytest fixture |
| 数据清理 | repos.md | `session.delete()` + ORM cascade |
| BDD 兼容 | api_client.md | httpx 包装，返回 Dict 适配 Gherkin |
