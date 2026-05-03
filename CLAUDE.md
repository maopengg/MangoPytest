# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

芒果测试平台 (mango_pytest) — 集 API/UI 自动化测试于一体的测试平台。当前主要工作是 **qfei_contract_api** BDD 模块，使用 pytest-bdd + Gherkin 中文语法编写针对合同管理系统 (CLM) 的 API 自动化测试。

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

### 目录结构

```
auto_tests/qfei_contract_api/
├── test_cases/migrated/   # Feature 文件（Gherkin 语法）
├── steps/migrated/        # 步骤定义层（按模块分包）
│   ├── common/            # 通用 fixtures
│   ├── api/               # API 请求步骤
│   ├── auth/              # 认证步骤
│   ├── data/              # 数据准备步骤
│   └── assertions/        # 断言步骤
├── data_factory/          # 数据工厂层
├── repos/                 # Repository 数据访问层
├── hooks/                 # 测试钩子（数据清理）
├── config/                # 多环境配置 (.env.dev/test/pre/prod)
├── api_client.py          # 客户端工厂
├── conftest.py            # pytest 全局配置
└── pytest.ini             # 标签定义
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

```python
from typing import Any, Dict
from pytest_bdd import when, parsers
from auto_tests.qfei_contract_api.config import settings
from core.utils import log

@when(parsers.cfparse('用户获取XX信息'), target_fixture="api_response")
def get_xx_step(logged_in_user: Dict[str, Any]):
    client = logged_in_user["client"]
    log.debug("开始获取XX信息")
    response = client.get("/clm/api/xx")
    log.debug(f"获取XX信息完成，状态码: {response.status_code}")
    return {
        "response": response,
        "status_code": response.status_code,
        "data": response.data,
    }
```

### 3. BDD 绑定文件规范

```python
import allure
from pytest_bdd import scenario

pytestmark = [
    allure.epic("智书合同API自动化测试"),
    allure.feature("迁移接口"),
    allure.story("模块名称"),
]

@allure.title("获取XX信息")
@scenario("./<name>.feature", "获取XX信息")
def test_获取XX信息():
    pass
```

### 4. 数据创建规范

- 使用 Factory 创建测试数据：`假如 存在"用户"`
- 测试数据以 `AUTO_` 开头，便于自动清理
- **禁止**在测试用例中直接调用 API 创建数据

### 5. 日志使用规范

- ✅ **优先使用 `debug`** — 大部分日志应该是 debug 级别
- ✅ 循环内部、频繁调用的方法必须使用 `debug`
- ✅ 关键业务节点（开始/结束/结果）使用 `info`
- ✅ 异常处理中使用 `error` 或 `warning`

## Running Tests

**必须使用 `.venv` 虚拟环境 + 设置 `ENV` 环境变量：**

```bash
# 运行单个测试（dev 环境）
ENV=dev .venv/Scripts/python -m pytest auto_tests/qfei_contract_api/test_cases/migrated/clm/tip_notice/test_tip_notice_bdd.py -v

# 运行整个模块
ENV=dev .venv/Scripts/python -m pytest auto_tests/qfei_contract_api/test_cases/migrated/clm/contract_reminder/ -v

# 按标签运行
ENV=dev .venv/Scripts/python -m pytest auto_tests/qfei_contract_api/ -m smoke

# 通过 main.py 执行完整测试
.venv/Scripts/python main.py

# 生成 Allure 报告
allure generate ./report/tmp -o ./report/html --clean
```

## Available Fixtures

| Fixture | Purpose |
|---------|---------|
| `logged_in_user` | CLM 已登录用户，包含 `client`, `token`, `user_id`, `tenant_id` |
| `open_api_client` | 开放 API 客户端（飞书认证） |
| `api_response` | 步骤间传递响应的 fixture |

## Available Assertion Steps

来自 `core/api/bdd_steps.py` 和 `core/dal/bdd_steps.py`：

| Gherkin 步骤 | 说明 |
|---|---|
| `响应状态码为 {code:d}` | 验证 HTTP 状态码 |
| `code 为 {expected:d}` | 验证 JSON body 中的 code 字段 |
| `success 为 true/false` | 验证 success 布尔字段 |
| `{path} 为 {expected}` | 通用路径断言 |
| `{path} 存在` | 验证路径不为 null |
| `{path} 包含 {expected}` | 验证字段包含子串 |
| `{path} 不为空` | 验证列表不为空 |
| `{path} 应该为 true/false` | DAL 布尔断言 |
| `{path} 应该等于 {expected}` | DAL 路径断言 |
| `{path} 应该包含 {expected}` | DAL 包含断言 |

## Required Test Marks (from pytest.ini)

每个测试文件应添加 `pytestmark`，包含合适的标签。已有标签：
`smoke`, `positive`, `negative`, `security`, `clm`, `openapi`, `ai`, `contract`, `tip_notice`, `home_page`, `approval_process`, `system_administration`, `auth`, `template`, `esign`, `vendor`, `payment`, `contract_reminder` 等。

## 禁止

- ❌ 在测试用例中直接调用 API 创建数据
- ❌ 在测试用例中写数据清理逻辑
- ❌ 在测试用例中定义配置常量
- ❌ 不遵守五层架构
