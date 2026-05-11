# BDD UI 模式 — 架构总览

## 定位

使用 pytest-bdd + Playwright 编写 UI 自动化测试。通过五层架构隔离职责，与 BDD API 模式共用同一套数据管理逻辑。

## 项目结构

```
auto_tests/<project>/
├── conftest.py          → conftest.md       # pytest 入口，自动发现 + 清理钩子
├── pytest.ini           → conftest.md       # markers 定义
│
├── test_cases/          → test_cases.md     # Feature 文件 + BDD 绑定
├── steps/               → steps.md          # @given / @when / @then
├── fixtures/            → fixtures.md       # pytest fixtures（浏览器、页面上下文）
├── page_object/         → page_object.md    # 页面对象（WebBaseObject 子类）
├── config/              → config.md         # 多环境配置 + 数据库初始化
├── data_factory/        → data_factory.md   # 数据工厂（Entity + Spec）
├── repos/               → repos.md          # Repository 数据访问 + 清理
└── hooks/               → hooks.md          # 会话级数据清理
```

## 五层架构

```
L5: test_cases/          Feature 文件（中文 Gherkin）+ BDD 绑定脚本
        │
L4: steps/ + fixtures/   步骤定义 + playwright fixtures
        │
L3: page_object/         页面对象（元素定位 + 操作封装）
     data_factory/       数据工厂（创建测试前置数据）
        │
L2: repos/               Repository（清理测试数据）
        │
L1: 浏览器（Playwright）+ 数据库
```

## 与 BDD API 的异同

| 维度 | BDD API | BDD UI |
|------|---------|--------|
| 用例层 L5 | Feature + BDD 绑定 | 同 |
| 步骤层 L4 | API 请求 + 断言步骤 | 页面操作 + 断言步骤 |
| Fixture | api_client, db_session | driver_object, base_data, db_session |
| 数据层 L3 | Entity + Spec 数据工厂 | page_object + Entity + Spec |
| 清理层 L2 | Repo + Hooks | 同（共用同一套数据逻辑） |
| 配置 | API URL | API URL + 浏览器配置 + 数据库 |

## 数据流

```
Feature: 假如 存在"用户" 且 用户已登录并进入首页
    ↓
步骤: 创建用户 → 数据工厂写库
    ↓
步骤: 打开浏览器 → page_object.goto(url)
    ↓
步骤: 操作页面元素 → page_object.click() / input()
    ↓
步骤: 断言 → assert 页面文本 / 元素状态
    ↓
清理: pytest_sessionstart → Repo.delete_by_pattern("AUTO_%")
```

## 关键文档

| 文档 | 内容 |
|------|------|
| config.md | 多环境配置 + 数据库初始化 |
| conftest.md | 自动发现 + 数据清理钩子 |
| test_cases.md | Feature 文件 + BDD 绑定 |
| steps.md | 页面操作步骤 + 断言步骤 |
| fixtures.md | 浏览器驱动 + 页面上下文 + 数据库会话 |
| page_object.md | 页面对象设计（元素定位 + 操作封装） |
| data_factory.md | Entity + Spec 数据工厂（与 API 共用逻辑） |
| repos.md | Repository 级联清理 |
| hooks.md | 会话级数据清理 |
