# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

芒果测试平台 (mango_pytest) — 集 API/UI 自动化测试于一体的测试平台。

## Architecture（必须遵守）

### 五层架构

```
L5: Feature 文件（Gherkin 中文语法）
    ↓
L4: Steps 步骤定义层（common/api/auth/data/assertions）
    ↓
L3: Data Factory（entities/factories/specs）
    ↓
L2: Repositories（按业务域分包，自动清理）
    ↓
L1: 数据库（MySQL）
```

## 测试用例编写规范

### 1. Feature 文件规范

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

### 2. 步骤定义规范

- 使用 `target_fixture="api_response"` 传递响应数据
- 返回 `{"response": response, "status_code": ..., "data": ...}` 格式
- 使用 `core.utils.log` 记录日志

### 3. 数据创建规范

- 使用 Factory 创建测试数据：`假如 存在"用户"`
- 测试数据以 `AUTO_` 开头，便于自动清理
- **禁止**在测试用例中直接调用 API 创建数据

### 4. 日志使用规范

- ✅ **优先使用 `debug`** — 大部分日志应该是 debug 级别
- ✅ 循环内部、频繁调用的方法必须使用 `debug`
- ✅ 关键业务节点（开始/结束/结果）使用 `info`
- ✅ 异常处理中使用 `error` 或 `warning`

## Running Tests

**必须使用 `.venv` 虚拟环境 + 设置 `ENV` 环境变量：**

```bash
# 通过 main.py 执行完整测试
ENV=dev .venv/Scripts/python main.py

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
