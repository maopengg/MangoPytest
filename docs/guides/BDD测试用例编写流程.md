# BDD 测试用例编写流程指南

## 概述

本文档描述了在 MangoPytest 框架中编写 BDD 测试用例的完整流程，以认证模块为例。

---

## 一、准备工作

### 1.1 理解需求

阅读测试用例文档，明确需要测试的功能点：

| 用例编号 | 用例标题 | 优先级 | 类型 |
|---------|---------|--------|------|
| TC-AUTH-0002 | 用户使用明文密码登录成功 | P1 | 正向 |
| TC-AUTH-0005 | 用户登录-用户名为空 | P1 | 负向/边界 |
| TC-AUTH-0007 | 新用户注册成功 | P0 | 正向 |

### 1.2 分析接口

确认接口信息：
- **接口路径**: `/auth/login`, `/auth/register`
- **请求方法**: POST
- **请求参数**: username, password, email, full_name, role
- **响应结构**: `{code, message, data}`

---

## 二、编写流程

### 步骤 1: 编写 Feature 文件 (L5)

**文件路径**: `auto_tests/api/bdd_api/test_cases/auth/test_auth.feature`

```gherkin
# language: zh-CN
# -*- coding: utf-8 -*-
功能: 用户认证
  作为系统用户
  我希望能够登录系统
  以便访问受保护的资源

@positive
场景: 使用明文密码登录成功
  当 用户使用用户名"testuser"和明文密码"password123"登录
  那么 登录应该成功

@negative @boundary
场景: 使用空用户名登录失败
  当 用户使用空用户名和密码"password123"登录
  那么 登录应该失败
  而且 应该返回错误码 400

@smoke @positive
场景: 新用户注册成功
  当 用户使用随机用户名和密码"password123"注册
  那么 注册应该成功
```

**编写要点**:
- 使用中文 Gherkin 语法
- 添加合适的标签 (`@smoke`, `@positive`, `@negative`, `@boundary`)
- 场景描述要清晰表达测试目的
- 使用 `而且` 连接多个断言

### 步骤 2: 编写步骤定义 (L4)

**文件路径**: `auto_tests/api/bdd_api/steps/auth/login.py`

#### 2.1 导入依赖

```python
# -*- coding: utf-8 -*-
import hashlib
import uuid
from typing import Dict, Any

from pytest_bdd import given, when, then, parsers
from core.utils import log
from mangotools.data_processor import DataProcessor

_data_processor = DataProcessor()
```

#### 2.2 编写 When 步骤

```python
@when(
    parsers.parse('用户使用用户名"{username}"和明文密码"{password}"登录'),
    target_fixture="login_response",
)
def user_login_with_plain_password_step(username: str, password: str, api_client):
    """用户使用明文密码登录步骤（系统应自动进行MD5加密）"""
    log.debug(f"使用明文密码登录: {username}")
    # 直接发送明文密码，让系统自动处理加密
    response = api_client.post(
        "/auth/login", {"username": username, "password": password}
    )
    log.debug(f"明文密码登录响应: {response.data}")
    return response
```

**编写要点**:
- 使用 `@when` 装饰器定义步骤
- 使用 `target_fixture` 指定返回的 fixture 名称
- 使用 `parsers.parse` 或 `parsers.re` 匹配 Gherkin 步骤
- 使用 `log.debug` 记录关键信息
- 返回响应对象供后续断言使用

#### 2.3 编写 Then 步骤

```python
@then(parsers.parse("登录应该成功"))
def login_should_succeed(login_response):
    """验证登录成功"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert response_data.get("code") == 200, f"登录失败: {response_data.get('message')}"
    assert response_data.get("data", {}).get("token") is not None


@then(parsers.parse('应该返回错误码 {error_code:d}'))
def should_return_error_code(error_code: int, login_response):
    """验证返回错误码"""
    response_data = (
        login_response.data if hasattr(login_response, "data") else login_response
    )
    assert (
        response_data.get("code") == error_code
    ), f"期望错误码 {error_code}，实际 {response_data.get('code')}"
```

**编写要点**:
- 使用 `@then` 装饰器定义断言步骤
- 从 fixture 参数获取响应数据
- 使用 `assert` 进行验证
- 提供清晰的错误信息

### 步骤 3: 添加 pytest 标记

**文件路径**: `auto_tests/api/bdd_api/pytest.ini`

确保所有使用的标记已注册：

```ini
[pytest]
markers =
    smoke: 冒烟测试
    positive: 正向测试
    negative: 负向测试
    boundary: 边界值测试
    integration: 集成测试
addopts = -v --tb=short --strict-markers
```

---

## 三、运行测试

### 3.1 运行单个测试文件

```bash
.venv\Scripts\python -m pytest auto_tests\bdd_api\test_cases\auth\test_auth.py -v
```

### 3.2 运行指定标签的测试

```bash
.venv\Scripts\python -m pytest auto_tests\bdd_api\test_cases\auth\test_auth.py -v -m "smoke"
```

### 3.3 查看测试报告

```bash
# 生成 Allure 报告
allure generate ./artifacts/reports/allure-results -o ./artifacts/reports/allure-html --clean
```

---

## 四、常见问题及解决方案

### 4.1 标记未注册错误

**错误信息**:
```
'boundary' not found in `markers` configuration option
```

**解决方案**: 在 `pytest.ini` 中添加标记定义

### 4.2 响应数据结构不匹配

**错误信息**:
```
KeyError: 'response'
```

**解决方案**: 检查步骤返回的数据结构是否与断言步骤期望的一致

### 4.3 用户名已存在

**错误信息**:
```
AssertionError: 注册失败: 用户名已存在
```

**解决方案**: 使用随机生成的用户名

```python
username = f"testuser_{uuid.uuid4().hex[:8]}"
```

### 4.4 缺少必填字段

**错误信息**:
```
ApiError: [422] API 错误: Field required
```

**解决方案**: 检查接口文档，确保所有必填字段都已提供

```python
email = _data_processor.character_email()
full_name = _data_processor.character_male_name()
response = api_client.post(
    "/auth/register",
    {
        "username": username,
        "password": password_md5,
        "role": "user",
        "email": email,
        "full_name": full_name,
    },
)
```

---

## 五、最佳实践

### 5.1 数据生成

使用 `mangotools.data_processor` 生成测试数据：

```python
from mangotools.data_processor import DataProcessor

_data_processor = DataProcessor()

# 生成随机数据
phone = _data_processor.character_phone()
email = _data_processor.character_email()
name = _data_processor.character_male_name()
uuid_str = _data_processor.str_uuid_no_dash()
```

### 5.2 日志记录

使用 `core.utils.log` 记录日志：

```python
from core.utils import log

log.debug(f"开始操作: {username}")  # 详细信息
log.info("关键节点")               # 重要信息
log.warning("警告信息")            # 警告
log.error("错误信息")              # 错误
```

### 5.3 代码组织

- 相关步骤放在同一文件
- 使用清晰的函数命名
- 添加文档字符串说明用途
- 遵循 PEP 8 编码规范

---

## 六、文件清单

完成一个用例需要修改/创建的文件：

| 文件 | 用途 | 层级 |
|------|------|------|
| `test_cases/auth/test_auth.feature` | Gherkin 场景定义 | L5 |
| `steps/auth/login.py` | 步骤定义实现 | L4 |
| `pytest.ini` | pytest 配置和标记 | 配置 |

---

## 七、参考文档

- [Gherkin 语法参考](https://cucumber.io/docs/gherkin/)
- [pytest-bdd 文档](https://pytest-bdd.readthedocs.io/)
- [项目架构文档](./第三方库/project_architecture.md)
- [DAL 断言指南](./dal_assertion_guide.md)
