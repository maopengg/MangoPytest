# Steps — 步骤定义层设计

## 职责

将 Gherkin 步骤文本映射为 Python 函数，是 Feature 文件和底层代码之间的胶水层。

## 设计思路

```
Feature: 当 GET "/users"
    ↓ parsers.re 匹配
def api_get_step(path) → 调 api_client.get(path) → 返回 Dict
    ↓ target_fixture="api_response"
Feature: 那么 响应状态码应该为 200
    ↓
def response_code_should_be_cn(api_response) → assert
```

## 目录结构

```
steps/
├── api/              # API 请求步骤（项目特定自定义）
├── auth/             # 登录相关步骤（项目特定）
└── __init__.py       # 导出项目特定步骤
```

**说明**：通用步骤已从 `core.bdd` 模块导入，不再在项目中重复定义。

## 通用步骤（core.bdd）

### 数据工厂步骤 (core.bdd.data_steps)

| 步骤 | 说明 | 示例 |
|------|------|------|
| `存在"{entity}" 作为 @{alias}` | 创建命名实体 | `假如 存在"产品" 作为 @产品A` |
| `存在"{entity}"` | 创建实体（使用中文名作为别名） | `假如 存在"产品"` |
| `存在 {count} 个"{entity}" 作为 @{alias}` | 批量创建实体 | `假如 存在 3 个"产品" 作为 @产品` |

### API 请求步骤 (core.bdd.api_steps)

| 步骤 | 说明 | 示例 |
|------|------|------|
| `GET "{path}"` | GET 请求 | `当 GET "/users/${{用户.id}}"` |
| `POST "{path}":` | POST 请求 | `当 POST "/orders": ...` |
| `PUT "{path}":` | PUT 请求 | `当 PUT "/orders/${{订单.id}}": ...` |
| `DELETE "{path}"` | DELETE 请求 | `当 DELETE "/orders/${{订单.id}}"` |
| `使用 @{alias} 发送 {method} 到 "{path}":` | 使用指定实体上下文 | `当使用 @产品 发送 POST 到 "/orders": ...` |

### 断言步骤 (core.bdd.assertion_steps)

| 步骤 | 说明 | 示例 |
|------|------|------|
| `响应状态码应该为 {code}` | 验证状态码 | `那么 响应状态码应该为 200` |
| `响应数据应该包含字段 "{field}"` | 验证字段存在 | `而且 响应数据应该包含字段 "order_no"` |
| `响应数据 "{field}" 应该为 "{value}"` | 验证字段值 | `而且 响应数据 "status" 应该为 "paid"` |
| `响应数据应该是列表` | 验证数据类型 | `而且 响应数据应该是列表` |
| `列表长度应该为 {length}` | 验证列表长度 | `而且 列表长度应该为 3` |
| `响应消息应该包含 "{text}"` | 验证消息内容 | `而且 响应消息应该包含 "成功"` |

## 配置方法

在项目的 `conftest.py` 中导入通用步骤：

```python
# conftest.py
from core.bdd.data_steps import *
from core.bdd.api_steps import *
from core.bdd.assertion_steps import *
```

## 项目特定步骤

如需添加项目特定的步骤，在 `steps/` 目录下创建：

```python
# steps/auth/login.py
from pytest_bdd import given, parsers

@given(parsers.parse('用户"{username}"已登录'))
def user_logged_in_step(username, api_client):
    # 自定义登录逻辑
    pass
```

然后在 `conftest.py` 中导入：

```python
from auto_tests.bdd_api_mock.steps.auth.login import *
```

## 步骤间数据传递

```
@when("GET /users", target_fixture="api_response")  → api_response = {...}
@then("响应状态码应该为 200")                          → 消费 api_response

@given('存在"产品" 作为 @产品A')                        → entity_context.add("产品A", entity)
@when('GET "/orders?id=${{产品A.id}}"')                 → 从 entity_context 获取
```

- `api_response` fixture：传递 API 响应
- `entity_context` fixture：传递创建的实体（支持多个命名实体）

## 占位符语法

| 格式 | 说明 | 示例 |
|------|------|------|
| `${{alias.attr}}` | 双括号格式 | `${{产品.id}}` |
| `@alias.attr` | @符号格式 | `@产品.id` |
| `{{attr}}` | 简写格式（配合 `使用 @xxx 发送`） | `{{id}}` |

## 参数解析

| 解析器 | 写法 | 示例 |
|--------|------|------|
| `parsers.parse` | `"{name}"` 花括号 | `用户"{username}"已登录` |
| `parsers.re` | `(?P<name>...)` 正则 | `GET "(?P<path>[^"]+)"` |

## 新增步骤模块

1. 在 `steps/` 下新建 `.py` 文件
2. 在 `conftest.py` 中导入新模块
3. 使用 `@when`、`@then`、`@given` 装饰器定义步骤
