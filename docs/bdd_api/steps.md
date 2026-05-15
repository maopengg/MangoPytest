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
├── common/           # 公共 fixture（api_response, created_entity）
├── api/              # GET/POST/PUT/DELETE 通用步骤
├── auth/             # 登录相关步骤
├── data/             # 数据创建步骤（调 data_factory）
└── assertions/       # 响应断言步骤
```

## 写法

### API 请求步骤

```python
# steps/api/base.py
from pytest_bdd import when, parsers

@when(parsers.re(r'GET "(?P<path>[^"]+)"'), target_fixture="api_response")
def api_get_step(path, mock_api_client):
    response = mock_api_client.get(path)
    return response   # target_fixture 会把返回值注入 api_response
```

**关键**：`target_fixture="api_response"` 让返回值自动成为 `api_response` fixture，后续断言步骤直接使用。

### 认证步骤

```python
# steps/auth/login.py
@given(parsers.parse('用户"{username}"已登录'), target_fixture="logged_in_user")
def user_logged_in_step(username):
    client = APIClient()
    resp = client.post("/auth/login", {"username": username, "password": md5(pwd)})
    return resp["data"]   # 包含 token、user_id 等
```

### 数据创建步骤

```python
# steps/data/factory.py
@given(parsers.parse('存在"{entity_name}"'))
def create_entity_step(entity_name, created_entity):
    factory_class = ENTITY_FACTORY_MAP[entity_name]  # 中文名 → Spec 类
    entity = factory_class()
    created_entity["id"] = entity.id
    created_entity["type"] = entity_name
```

### 断言步骤

```python
# steps/assertions/response.py
@then(parsers.parse("响应状态码应该为 {expected_code:d}"))
def response_code_should_be_cn(expected_code, api_response):
    assert api_response.get("code") == expected_code

@then(parsers.parse("响应消息应该包含 {text}"))
def response_message_should_contain(text, api_response):
    assert text in api_response.get("message", "")
```

## 步骤间数据传递

```
@when("GET /users", target_fixture="api_response")  → api_response = {...}
@then("响应状态码应该为 200")                          → 消费 api_response

@given('存在"用户"')                                   → created_entity = {"id": 1, "type": "用户"}
@when('GET "/users?id=${user.id}"')                    → 消费 created_entity
```

- `api_response` fixture：传递 API 响应
- `created_entity` fixture：传递创建的实体

## 参数解析

| 解析器 | 写法 | 示例 |
|--------|------|------|
| `parsers.parse` | `"{name}"` 花括号 | `用户"{username}"已登录` |
| `parsers.re` | `(?P<name>...)` 正则 | `GET "(?P<path>[^"]+)"` |

## 新增步骤模块

1. 在 `steps/` 下新建 `.py` 文件
2. conftest 自动发现，无需手动注册
