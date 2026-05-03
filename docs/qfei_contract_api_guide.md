# 智书合同 API 自动化测试 — 开发指南

## 1. 架构概览

```
六层架构：

  Feature 文件（Gherkin 中文语法）
       │
  Step 步骤定义层（common / api / auth / data / assertions）
       │
  Data Factory 数据工厂层（entities → specs → factories）
       │
  Repositories 数据访问层（按业务域分包）
       │
  数据库（MySQL）
```

目录结构：

```
auto_tests/qfei_contract_api/
├── __init__.py              # 项目元数据
├── conftest.py              # pytest 配置（步骤/fixture 自动发现）
├── api_client.py            # 客户端工厂函数
├── config/                  # 多环境配置
│   ├── settings.py          #   Pydantic 字段定义
│   ├── __init__.py          #   环境解析
│   └── .env.dev/test/pre    #   环境配置值
├── fixtures/                # pytest fixture
│   ├── auth.py              #   登录（session 级缓存）
│   ├── clients.py           #   OpenAPI / AI 客户端
│   └── bdd.py               #   BDD 响应传递
├── steps/migrated/          # 步骤定义（自动发现）
├── test_cases/migrated/     # Feature 文件 + BDD 绑定
├── data_factory/            # 数据工厂
├── repos/                   # 数据库访问
├── hooks/                   # 测试钩子
└── data/uploads/            # 上传测试文件
```

---

## 2. 快速开始

### 2.1 运行测试

```bash
# 单个测试文件
ENV=dev .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_api/test_cases/migrated/clm/home_page/test_draft_bdd.py -v

# 整个模块
ENV=dev .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_api/test_cases/migrated/clm/home_page/ -v

# 按标签运行
ENV=dev .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_api/ -m smoke

# 从 main.py 运行（批量）
.venv/Scripts/python main.py
```

### 2.2 环境切换

| ENV 值 | 环境 |
|--------|------|
| `dev` | 开发环境 |
| `test` | 测试环境 |
| `pre` | 预发布环境 |
| `prod` | 生产环境 |

也可以在 `main.py` 中修改 `test_environment` 枚举值切换。

---

## 3. Feature 文件编写

### 3.1 基本语法

```gherkin
# language: zh-CN
功能: 模块名称
  迁移自: <原始JSON文件路径>

  背景:
    假如 用户已登录系统

  场景: 获取XX信息
    当 用户获取XX信息
    那么 响应状态码为 200
    并且 code 为 200
    并且 success 为 true
```

### 3.2 场景大纲（参数化）

```gherkin
  场景大纲: 查询元素类型
    当 用户查询元素类型，值类型为 <value_type>
    那么 响应状态码为 200
    并且 code 为 200

    例子:
      | value_type |
      | EMPLOYEE_COLLECTION |
      | BOOLEAN      |
      | NUMBER       |
```

### 3.3 规范要点

- 每个场景对应一个接口测试
- 断言至少包含状态码和业务 code
- 负面测试使用 `code 为 <错误码>` 而非 `响应状态码为 200`

---

## 4. Step 步骤定义编写

### 4.1 基本模式

```python
from typing import Any, Dict
from pytest_bdd import when, parsers
from core.utils import log

@when(parsers.cfparse('用户获取XX信息'), target_fixture="api_response")
def get_xx_step(logged_in_user: Dict[str, Any]):
    client = logged_in_user["client"]
    log.debug("开始获取XX信息")

    response = client.get("/clm/api/xx")

    return {
        "response": response,
        "status_code": response.status_code,
        "data": response.data,
    }
```

### 4.2 关键约定

- **fixture 输出格式** — 必须返回 `{"response": ..., "status_code": ..., "data": ...}`
- **target_fixture** — 使用 `"api_response"` 传递给 Then 步骤
- **日志** — 关键节点用 `log.debug`
- **文件位置** — 步骤文件放在 `steps/migrated/<模块>/` 下，会被自动发现

### 4.3 跨步骤共享状态

如果多个步骤需要传递动态值（如上传文件后的 fileId），使用模块级字典：

```python
# 模块顶部定义
_workflow_context = {"file_id": None, "task_id": None}

@when('用户上传文件', target_fixture="api_response")
def upload(logged_in_user):
    response = logged_in_user["client"].upload(...)
    _workflow_context["file_id"] = response.data["data"]["fileId"]
    return {...}

@when('用户查询文件信息', target_fixture="api_response")
def query(logged_in_user):
    file_id = _workflow_context["file_id"]
    response = logged_in_user["client"].get(f"/api/file/{file_id}")
    return {...}
```

---

## 5. APIClient 客户端工厂

文件：`api_client.py`

```python
from auto_tests.qfei_contract_api.api_client import (
    get_clm_client,      # CLM 内部 API — Cookie 认证
    get_open_client,     # 开放 API — 飞书 token 认证
    get_ai_client,       # AI 服务 — 同 CLM，可能不同 Host
    get_ai_open_client,  # AI 开放 API — 独立飞书应用认证
)
```

### 5.1 认证机制

| 客户端 | 认证方式 | 适用场景 |
|--------|---------|---------|
| `get_clm_client()` | Cookie（zs_session + clm_csrf_token） | 合同管理系统内部接口 |
| `get_open_client()` | 飞书 tenant_access_token | 对外开放 API |
| `get_ai_client()` | 同 CLM（Cookie） | AI 审查/提取服务 |
| `get_ai_open_client()` | 飞书 tenant_access_token（独立应用） | AI 开放 API |

---

## 6. Fixture 清单

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `logged_in_user` | function（session 缓存） | 已登录用户，含 `client`、`token`、`user_id`、`tenant_id` |
| `open_api_client` | function（session 缓存） | 开放 API 客户端，已认证 |
| `ai_open_client` | function（session 缓存） | AI 开放 API 客户端 |
| `api_response` | function | 步骤间传递响应的 fixture |
| `contract_api_settings` | session | 合同 API 配置 |

### 6.1 Session 缓存机制

`logged_in_user` 底层依赖 `_session_logged_in_user`（session 级），整个测试会话只登录一次，所有测试共享同一个 client。

---

## 7. 配置管理

### 7.1 基础设施配置

| 字段 | 说明 |
|------|------|
| `HOST` | CLM 主机地址 |
| `TENANT_ID` | 租户 ID |
| `ZS_TOKEN` | 用户认证 Token |
| `APP_ID` / `APP_SECRET` | 开放 API 飞书应用凭证 |
| `APP_ID_AI_OPEN` / `APP_SECRET_AI_OPEN` | AI 开放 API 飞书应用凭证 |
| `CSRF_TOKEN_COOKIE` / `CSRF_TOKEN_HEADER` | CSRF Token |

### 7.2 业务 ID 配置

| 字段 | 说明 |
|------|------|
| `BUSINESS_ID` | 业务 ID |
| `CONTRACT_ID1` | 合同 ID |
| `RULE_GROUP_ID` | 规则组 ID |
| `PROCESS_INSTANCE_ID` | 流程实例 ID |
| ... | 共约 20 个业务相关字段 |

### 7.3 新增配置

1. 在 `settings.py` 中添加 `Field` 定义
2. 在 `.env.dev/test/pre/prod` 中添加对应的值
3. 在代码中通过 `settings.新字段` 使用

---

## 8. 如何新增一个测试模块（完整示例）

假设我们要新增"合同标签管理"模块的测试。

### 8.1 创建 Feature 文件

`test_cases/migrated/clm/contract_label/contract_label.feature`：

```gherkin
# language: zh-CN
功能: 合同标签管理
  场景: 获取合同标签列表
    假如 用户已登录系统
    当 用户获取合同标签列表
    那么 响应状态码为 200
    并且 code 为 200
    并且 success 为 true
```

### 8.2 创建步骤定义

`steps/migrated/clm/contract_label/contract_label.py`：

```python
from typing import Any, Dict
from pytest_bdd import when, parsers
from core.utils import log

@when(parsers.cfparse('用户获取合同标签列表'), target_fixture="api_response")
def get_contract_labels(logged_in_user: Dict[str, Any]):
    client = logged_in_user["client"]
    log.debug("获取合同标签列表")
    response = client.get("/clm/api/contract/label/list")
    return {
        "response": response,
        "status_code": response.status_code,
        "data": response.data,
    }
```

### 8.3 创建 BDD 绑定文件

`test_cases/migrated/clm/contract_label/test_contract_label_bdd.py`：

```python
import allure
from pytest_bdd import scenario

pytestmark = [
    allure.epic("智书合同API自动化测试"),
    allure.feature("迁移接口"),
    allure.story("合同标签管理"),
]

@allure.title("获取合同标签列表")
@scenario("./contract_label.feature", "获取合同标签列表")
def test_获取合同标签列表():
    pass
```

### 8.4 创建 __init__.py

在 `steps/migrated/clm/contract_label/` 目录下创建 `__init__.py`（conftest 自动发现需要）。

### 8.5 运行测试

```bash
ENV=dev .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_api/test_cases/migrated/clm/contract_label/ -v
```

不需要改 conftest.py — 自动发现会扫描到新模块。

---

## 9. 测试标签

文件：`pytest.ini`

常用标签用法：

```bash
# 仅跑冒烟测试
pytest -m smoke

# 仅跑特定模块
pytest -m clm

# 组合条件
pytest -m "clm and positive"
```

在 BDD 绑定文件中设置：

```python
pytestmark = [
    allure.epic("智书合同API自动化测试"),
    allure.feature("迁移接口"),
    allure.story("模块名称"),
]
```

在 Feature 文件中设置：

```gherkin
  @smoke @positive
  场景: ...
```

---

## 10. 故障排查

**"客户端未初始化" 或 `logged_in_user` 数据异常？**
- 确认 Feature 文件有 `假如 用户已登录系统` 背景步骤
- 确认使用了正确的 fixture 名称

**接口返回 401？**
- 检查 `ENV` 环境变量是否匹配当前环境
- 检查 .env 中的 Token 是否过期
- 确认 VPN 已连接

**新增步骤提示 StepDefinitionNotFoundError？**
- 确认步骤模块在 `steps/migrated/` 下且文件名不以 `__init__` 结尾
- 确认对应的目录有 `__init__.py`
- 确认 `parsers.cfparse` 中的模式匹配 Feature 文件中的文本

**测试数据残留？**
- 使用 `AUTO_` 前缀命名的测试数据会被 hooks 自动清理
- 通过 `data_factory` 创建的数据会自动注册清理回调
