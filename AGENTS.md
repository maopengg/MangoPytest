# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

芒果测试平台 (mango_pytest) — 集 API/UI 自动化测试于一体的测试平台。

## 内部包使用规范（必须遵守）

本项目与 `/Users/mango/code/qfei-auto-platform` 使用同一套芒果内部包：

| 源码仓库 | Python 包 | 本项目联调版本 |
|---|---|---|
| `/Users/mango/code/mango_tools` | `mangotools` | `2.0.8` |
| `/Users/mango/code/mango_automation` | `mangoautomation` | `2.0.4` |

- `mangotools` 和 `mangoautomation` 禁止从 PyPI 安装；PyPI 版本是旧实现。
- 公共三方依赖维护在 `requirements.txt`，内部包只维护在
  `requirements-local.txt`，使用本项目 `local_packages/` 中与
  `qfei-auto-platform` 一致的 wheel。
- 只查看内部包源码时无需同步。若修改了内部包源码，必须先在对应源码仓库运行
  `sync_local_package.py`，再将生成的 wheel 同步到本项目 `local_packages/` 并更新版本声明。
- `mangotools` 按职责从具体模块导入，例如 `data_processor`、`decorator`、
  `models`、`exceptions`、`enums`；禁止依赖未声明的兼容导出。
- `mangoautomation` 统一从 `mangoautomation.uidrives`（复数）导入；禁止使用
  已移除的 `mangoautomation.uidrive`。
- Web 生命周期由 `WebDriverFactory` 创建的 `SyncWebRuntime` / `AsyncWebRuntime`
  管理；`BaseData` 通过 `bind_web(runtime, context, page)` 绑定上下文。
- 新代码禁止使用旧的 `DriverObject` 聚合器。pytest 同步 UI 用例使用
  `SyncWebRuntime`，异步执行器才使用 `AsyncWebRuntime` 与 `AsyncElement`。
- 包异常分别捕获 `mangoautomation.exceptions.MangoAutomationError` 和
  `mangotools.exceptions.MangoToolsError`，不要用宽泛异常替代可识别的业务异常。

## Architecture（必须遵守）

API/UI Demo 按项目定位使用不同的五层架构，禁止把不同模式混用：

### 轻量 API 项目（`simple_api`）

```text
Tests → Fixture → Factory + Repository → 公共 HTTP 客户端
```

- `simple_api` 禁止新增 Feature、Steps 或 `pytest_bdd` 依赖。
- 它只演示少量基础 HTTP Case，不承担大型项目业务编排。

### BDD 项目（`bdd_api`）

```
L5: Feature 文件（Gherkin 中文语法）
    ↓
L4: Steps 步骤定义层（common/api/auth/data/assertions）
    ↓
L3: Data Factory（entities/factories/specs）
    ↓
L2: Repositories（按业务域分包，自动清理）
    ↓
L1: 公共协议客户端 / 数据库 Gateway
```

### 纯 pytest 项目（`pytest_api`）

```
L5: Tests（pytest 测试、marks、参数化与断言）
    ↓
L4: Services / Workflows（业务场景与跨协议编排）
    ↓
L3: Data Factory（entities/factories/specs）
    ↓
L2: Repositories（按业务域分包，自动清理）
    ↓
L1: 公共协议客户端 / 数据库 Gateway
```

- `pytest_api` 禁止新增 Feature、Steps 或 `pytest_bdd` 依赖。
- Tests 和 Steps 均禁止直接访问协议客户端私有字段。
- HTTP、WebSocket、SSE、MCP、gRPC 统一复用 `auto_tests/common/mango_mock/`。

### BDD UI 项目（`bdd_ui`）

```
L5: Feature 文件（中文业务 Gherkin）
    ↓
L4: Steps（领域步骤、公共步骤、断言步骤）
    ↓
L3: Flows + Data Factory（entities/factories/specs/scenarios）
    ↓
L2: Page Objects + Repositories + 本地 Excel 元素仓库
    ↓
L1: SyncWebRuntime / 公共协议客户端 / 数据库 Gateway
```

### 纯 pytest UI 项目（`pytest_ui`）

```
L5: Tests（pytest 测试、marks、参数化与业务断言）
    ↓
L4: Flows（跨页面业务场景编排）
    ↓
L3: Data Factory（entities/factories/specs/scenarios）
    ↓
L2: Page Objects + Repositories + 本地 Excel 元素仓库
    ↓
L1: SyncWebRuntime / 公共协议客户端 / 数据库 Gateway
```

- `pytest_ui` 禁止新增 Feature、Steps 或 `pytest_bdd` 依赖。
- `bdd_ui` 的业务 Feature 禁止使用“执行 UI-xxx 用例”式编号转发步骤；
  框架操作能力矩阵必须放在独立的 `features/capabilities/` 下。
- UI 元素只读取各项目自己的本地 Excel，禁止依赖飞书和跨 Demo 元素文件。
- Tests、Steps 和 Flows 禁止直接操作 Playwright Locator；页面行为必须进入 Page Object。
- Page Object 禁止创建测试数据或编写 pytest 业务断言。

## 测试用例编写规范

### 1. BDD Feature 文件规范

- 使用中文 Gherkin 语法（`# language: zh-CN`）
- 每个场景对应一个接口测试
- 断言至少包含状态码和业务 code

```gherkin
# language: zh-CN
功能: 模块名称
  场景: 获取XX信息
    当 用户获取XX信息
    那么 响应状态码为 200
    并且 code 为 200
    并且 success 为 true
```

### 2. BDD 步骤定义规范

- 使用 `target_fixture="api_response"` 传递响应数据
- 返回 `{"response": response, "status_code": ..., "data": ...}` 格式
- 使用 `core.utils.log` 记录日志

### 3. 数据创建规范

- 使用 Factory 创建测试数据：`假如 存在"用户"`
- 测试数据以 `AUTO_` 开头，便于自动清理
- **禁止**在测试用例中直接调用 API 创建数据

### 4. 纯 pytest 用例规范

- 测试函数只调用 Factory、Repository 或 Service 的公开方法。
- 每条用例保留 Case ID，并使用 pytest mark / Allure 元数据关联。
- 请求和响应优先使用 Pydantic 强类型模型；边界场景使用参数化。
- 前置数据通过 fixture + Factory 创建，清理由 fixture + Repository 完成。
- 禁止使用按 Case ID 编号区间路由的集中执行器。

### 5. 日志使用规范

- ✅ **优先使用 `debug`** — 大部分日志应该是 debug 级别
- ✅ 循环内部、频繁调用的方法必须使用 `debug`
- ✅ 关键业务节点（开始/结束/结果）使用 `info`
- ✅ 异常处理中使用 `error` 或 `warning`

## Running Tests

**必须使用 `.venv` 虚拟环境 + 设置 `ENV` 环境变量：**

```bash
# 安装公共依赖和与 qfei-auto-platform 一致的本地内部包
.venv/bin/python -m pip install -r requirements.txt -r requirements-local.txt

# 通过 main.py 执行完整测试
ENV=test .venv/bin/python main.py --project pytest_api

# 生成 Allure 报告
allure generate ./artifacts/reports/allure-results -o ./artifacts/reports/allure-html --clean
```

## Available Fixtures

| Fixture | Purpose |
|---------|---------|
| `api_response` | 步骤间传递响应的 fixture |

## Available Assertion Steps

**强制使用 DAL 断言（`core/dal/bdd_steps.py`）**：

| Gherkin 步骤 | 说明 |
|---|---|
| `响应状态码应该为 {code}` | 验证 HTTP 状态码 |
| `响应字段 "{field}" 应该为 "{value}"` | 验证响应 JSON 字段 |
| `响应数据 "{field}" 应该为 "{value}"` | 验证 data 内业务数据 |
| `响应数据应该包含字段 "{field}"` | 验证字段存在性 |
| `响应数据应该是列表` | 验证数据类型 |
| `列表长度应该为 {length}` | 验证列表长度 |
| `响应消息应该包含 "{text}"` | 验证消息内容 |

**DAL 表达式断言（推荐）**：
```gherkin
那么 响应应该为:
  """
  status_code = 200
  body.code = 200
  body.data.size > 0
  """
```

## Required Test Marks (from pytest.ini)

每个测试文件应添加 `pytestmark`，包含合适的标签。已有标签：
`smoke`, `positive`, `negative`, `security`, `integration`, `auth` 等。

## 禁止

- ❌ 在测试用例中直接调用 API 创建数据
- ❌ 在测试用例中写数据清理逻辑
- ❌ 在测试用例中定义配置常量
- ❌ 不遵守五层架构
