# Core BDD 模块

通用的 BDD 测试框架，支持多项目复用。

## 目录结构

```
core/bdd/
├── __init__.py           # 模块导出
├── context.py            # 实体上下文管理
├── placeholder.py        # 占位符替换工具
├── data_steps.py         # 数据工厂步骤
├── api_steps.py          # API 请求步骤
├── assertion_steps.py    # 断言步骤
├── conftest_example.py   # conftest.py 配置示例
└── README.md            # 本文档
```

## 核心特性

### 1. 显式实体命名

```gherkin
假如 存在"产品" 作为 @产品A
假如 存在"用户" 作为 @买家
```

### 2. 多格式占位符支持

- `${'{alias.attr}'}` - 双括号格式
- `@`alias`.`attr - 简洁格式
- `{{attr}}` - 当前实体简写（配合 `使用 @xxx 发送` 步骤）

### 3. 多项目支持

每个项目只需提供：

- `entity_factory_map` fixture - 实体名到 Factory 的映射
- `db_session` fixture - 数据库会话
- `api_client` fixture - API 客户端

## 快速开始

### 1. 配置项目 conftest.py

```python
# auto_tests/<project>/conftest.py

import pytest
from core.bdd.data_steps import *
from core.bdd.api_steps import *
from core.bdd.assertion_steps import *


@pytest.fixture(scope="session")
def entity_factory_map():
    from auto_tests.<project>.data_factory.specs import (
        UserSpec, ProductSpec, OrderSpec,
    )
    return {
        "用户": UserSpec,
        "产品": ProductSpec,
        "订单": OrderSpec,
    }


@pytest.fixture(scope="function")
def db_session():
    from auto_tests.<project>.config import settings
    session = settings.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def api_client():
    from core.api.client import APIClient
    from auto_tests.<project>.config import settings
    return APIClient(base_url=settings.BASE_URL)
```

### 2. 编写 Feature 文件

```gherkin
# language: zh-CN
功能: 订单管理

  场景: 创建包含多个产品的订单
    假如 存在"产品" 作为 @手机
    而且 存在"产品" 作为 @耳机
    而且 存在"用户" 作为 @买家
    
    当 POST "/orders":
      """
      {
        "buyer_id": ${'{买家.id}'},
        "items": [
          {"product_id": ${'{手机.id}'}, "qty": 1},
          {"product_id": ${'{耳机.id}'}, "qty": 2}
        ]
      }
      """
    那么 响应状态码应该为 200
    而且 响应数据应该包含字段 "order_no"
```

## 支持的步骤

### 数据工厂步骤 (data\_steps.py)

| 步骤                                   | 说明              | 示例                     |
| ------------------------------------ | --------------- | ---------------------- |
| `存在"{entity}" 作为 @{alias}`           | 创建命名实体          | `假如 存在"产品" 作为 @产品A`    |
| `存在"{entity}"`                       | 创建实体（使用中文名作为别名） | `假如 存在"产品"`            |
| `存在 {count} 个"{entity}" 作为 @{alias}` | 批量创建实体          | `假如 存在 3 个"产品" 作为 @产品` |

### API 请求步骤 (api\_steps.py)

| 步骤                                    | 说明        | 示例                                  |
| ------------------------------------- | --------- | ----------------------------------- |
| `GET "{path}"`                        | GET 请求    | `当 GET "/users/${'{用户.id}'}"`       |
| `POST "{path}":`                      | POST 请求   | `当 POST "/orders": ...`             |
| `PUT "{path}":`                       | PUT 请求    | `当 PUT "/orders/${'{订单.id}'}": ...` |
| `DELETE "{path}"`                     | DELETE 请求 | `当 DELETE "/orders/${'{订单.id}'}"`   |
| `使用 @{alias} 发送 {method} 到 "{path}":` | 使用指定实体上下文 | `当使用 @产品 发送 POST 到 "/orders": ...`  |

### 断言步骤 (assertion\_steps.py)

| 步骤                             | 说明     | 示例                            |
| ------------------------------ | ------ | ----------------------------- |
| `响应状态码应该为 {code}`              | 验证状态码  | `那么 响应状态码应该为 200`             |
| `响应数据应该包含字段 "{field}"`         | 验证字段存在 | `而且 响应数据应该包含字段 "order_no"`    |
| `响应数据 "{field}" 应该为 "{value}"` | 验证字段值  | `而且 响应数据 "status" 应该为 "paid"` |
| `响应数据应该是列表`                    | 验证数据类型 | `而且 响应数据应该是列表`                |
| `列表长度应该为 {length}`             | 验证列表长度 | `而且 列表长度应该为 3`                |
| `响应消息应该包含 "{text}"`            | 验证消息内容 | `而且 响应消息应该包含 "成功"`            |

## API 参考

### EntityContext

```python
from core.bdd import EntityContext

context = EntityContext()

# 添加实体
context.add("产品A", product_entity)

# 获取实体
entity = context.get("产品A")

# 获取属性
product_id = context.get_attr("产品A", "id")

# 检查存在
if context.has("产品A"):
    ...

# 列出所有别名
aliases = context.list_aliases()

# 构建占位符上下文
placeholder_context = context.build_placeholder_context(
    '{"id": ${'"'"'产品A.id'"'"'}}'
)
# 返回: {"产品A.id": 123}
```

### PlaceholderReplacer

```python
from core.bdd import PlaceholderReplacer, replace_placeholders

# 方式1: 使用类
replacer = PlaceholderReplacer({"user.id": 123, "product.id": 456})
result = replacer.replace('{"user_id": ${'"'"'user.id'"'"'}}')
# 结果: {"user_id": 123}

# 方式2: 使用便捷函数
result = replace_placeholders(
    '{"user_id": ${'"'"'user.id'"'"'}}',
    {"user.id": 123}
)
```

## 占位符格式

### 1. 双括号格式（推荐）

```json
{
  "product_id": ${'{产品.id}'},
  "user_id": ${'{用户.id}'}
}
```

### 2. @符号格式（简洁）

```json
{
  "product_id": @`产品`.`id`,
  "user_id": @`用户`.`id`
}
```

### 3. 简写格式（配合 `使用 @xxx 发送`）

```gherkin
当使用 @产品 发送 POST 到 "/orders":
  """
  {
    "product_id": {{id}},
    "product_name": {{name}}
  }
  """
```

## 多项目配置示例

### 项目 A: bdd\_api\_mock

```python
# auto_tests/api/bdd_api/conftest.py

import pytest
from core.bdd.data_steps import *
from core.bdd.api_steps import *
from core.bdd.assertion_steps import *

@pytest.fixture(scope="session")
def entity_factory_map():
    from auto_tests.api.bdd_api.data_factory.specs import (
        UserSpec, ProductSpec, OrderSpec,
    )
    return {
        "用户": UserSpec,
        "产品": ProductSpec,
        "订单": OrderSpec,
    }

@pytest.fixture(scope="function")
def db_session():
    from auto_tests.api.bdd_api.config import settings
    session = settings.SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="session")
def api_client():
    from core.api.client import APIClient
    from auto_tests.api.bdd_api.config import settings
    return APIClient(base_url=settings.BASE_URL)
```

## 迁移指南

### 从旧方案迁移

旧方案使用全局缓存 `_entity_cache`，新方案使用 `entity_context` fixture。

**旧代码:**

```python
# steps/data/factory.py
_entity_cache = {}

def create_entity_step(entity_name):
    entity = factory_class.create_sync(db_session)
    _entity_cache[entity_name] = entity
```

**新代码:**

```python
# 直接使用 core.bdd.data_steps 中的步骤
# 无需自己实现，只需在 conftest.py 中导入
from core.bdd.data_steps import *
```

**Feature 文件变化:**

旧:

```gherkin
假如 存在"产品"
当 POST "/orders":
  """
  {"product_id": ${'{product.id}'}}
  """
```

新:

```gherkin
假如 存在"产品" 作为 @产品A
当 POST "/orders":
  """
  {"product_id": ${'{产品A.id}'}}
  """
```

## 最佳实践

1. **始终使用显式别名** - 提高可读性，避免歧义
2. **使用中文别名** - 与 Feature 文件语言保持一致
3. **一个场景内保持命名一致** - 避免混用中英文别名
4. **及时清理** - 场景结束后实体上下文自动清理
5. **错误处理** - 框架提供友好的错误提示，帮助定位问题
