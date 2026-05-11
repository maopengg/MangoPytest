# DAL (Data Assertion Language) - 数据断言语言

DAL 是一个用于测试数据验证的表达式语言，灵感来源于 Java TestCharm DAL。它提供了简洁、强大的语法来验证各种数据结构。

## 目录

- [快速开始](#快速开始)
- [基础用法](#基础用法)
- [数据访问](#数据访问)
- [比较操作符](#比较操作符)
- [逻辑操作符](#逻辑操作符)
- [对象验证](#对象验证)
- [列表验证](#列表验证)
- [表格验证](#表格验证)
- [通配符](#通配符)
- [元数据访问](#元数据访问)
- [Schema 验证](#schema-验证)
- [异步等待](#异步等待)
- [自定义操作符](#自定义操作符)
- [pytest-bdd 集成](#pytest-bdd-集成)

## 快速开始

```python
from mangotools.dal import expect

# 基础断言
expect(1).should("= 1")
expect("hello").should("= 'hello'")

# 对象断言
data = {"name": "张三", "age": 25}
expect(data).should(": { name: '张三', age: 25 }")

# 列表断言
expect([1, 2, 3]).should(".size = 3")

# 表格断言
expect([{"id": 1}, {"id": 2}]).should("""
    | id |
    | 1  |
    | 2  |
""")
```

## 基础用法

### 导入模块

```python
from mangotools.dal import expect, get
from mangotools.dal.schema import register_schema, validate_schema
```

### 基本断言

```python
# 严格相等
expect(1).should("= 1")
expect("hello").should("= 'hello'")
expect(True).should("= True")
expect(None).should("= null")

# 不等于
expect(1).should("!= 2")

# 比较操作
expect(10).should("> 5")
expect(10).should("< 20")
expect(10).should(">= 10")
expect(10).should("<= 10")
```

### 隐式根对象访问

当表达式以操作符开头时，会自动访问根对象：

```python
data = {"name": "张三", "age": 25}

# 以下两种写法等价
expect(data).should("name = '张三'")
expect(data).should("= '张三'")  # 如果 data 本身就是 "张三"
```

## 数据访问

### 属性访问

```python
data = {"user": {"name": "张三", "email": "test@test.com"}}

# 点号访问
expect(data).should("user.name = '张三'")

# 嵌套访问
expect(data).should("user.email = 'test@test.com'")
```

### 索引访问

```python
# 列表索引
data = [{"id": 1}, {"id": 2}]
expect(data).should("[0].id = 1")
expect(data).should("[1].id = 2")

# 字典键访问
data = {"items": [{"name": "A"}, {"name": "B"}]}
expect(data).should("items[0].name = 'A'")
```

### 使用 get 访问器

```python
from mangotools.dal import get

data = {"user": {"name": "张三", "age": 25}}

# 获取属性值
name = get(data).property("user.name").value()  # "张三"
age = get(data).property("user.age").value()    # 25

# 可选访问（不存在返回 None）
phone = get(data).property("user.phone").optional()  # None
```

## 比较操作符

### 严格相等 (=)

类型和值都必须相同：

```python
expect(1).should("= 1")       # 通过
expect(1).should("= 1.0")     # 失败，类型不同
expect("1").should("= '1'")   # 通过
```

### 宽容匹配 (:)

类型可以不同，值相等即可：

```python
expect(1).should(": 1.0")     # 通过，1 == 1.0
expect("123").should(": 123") # 通过，"123" 转为 123
```

### 正则匹配

```python
expect("hello world").should("= /hello.*/")
expect("ORD-001").should("= /ORD-\d+/")

# 使用 match 操作符
expect("hello").should("~ /ell/")
```

### 字符串匹配

```python
# contains - 包含
expect("hello world").should("contains 'world'")

# starts with - 以...开头
expect("hello world").should("starts with 'hello'")

# ends with - 以...结尾
expect("hello world").should("ends with 'world'")
```

## 逻辑操作符

### 逻辑与 (and)

```python
expect(5).should("> 3 and < 10")
expect("active").should("= 'active' and != 'deleted'")
```

### 逻辑或 (or)

```python
expect("active").should("= 'active' or = 'pending'")
```

### 逻辑非 (not)

```python
expect("deleted").should("not = 'active'")
expect(5).should("not = 7")
```

### 复杂逻辑组合

```python
expect(5).should("> 3 and < 10 and not = 7")
expect("status").should("= 'active' or = 'pending' or = 'draft'")
```

## 对象验证

### 宽容对象验证 (: {...})

只验证指定的字段，忽略其他字段：

```python
user = {"name": "张三", "age": 25, "email": "test@test.com"}

expect(user).should("""
    : {
        name: '张三'
        age: 25
    }
""")
# 通过，email 字段被忽略
```

### 严格对象验证 (= {...})

验证所有字段，不允许有多余字段：

```python
user = {"name": "张三", "age": 25}

expect(user).should("""
    = {
        name: '张三'
        age: 25
    }
""")
# 通过

# 以下会失败，因为有 email 多余字段
user_with_email = {"name": "张三", "age": 25, "email": "test@test.com"}
# expect(user_with_email).should("= { name: '张三', age: 25 }")  # 失败
```

### 嵌套对象验证

```python
user = {
    "name": "张三",
    "address": {
        "city": "北京",
        "zip": "100000"
    }
}

expect(user).should("""
    : {
        name: '张三'
        address.city: '北京'
        address.zip: '100000'
    }
""")
```

### 字段存在性检查

```python
user = {"name": "张三", "email": "test@test.com"}

expect(user).should("""
    : {
        name?          # name 必须存在
        phone?:        # phone 可选
    }
""")
```

## 列表验证

### 列表大小

```python
orders = [{"id": 1}, {"id": 2}]
expect(orders).should(".size = 2")
expect(orders).should("::size = 2")  # 使用元数据访问
```

### 列表索引访问

```python
orders = [{"id": 1}, {"id": 2}]
expect(orders).should("[0].id = 1")
expect(orders).should("[1].id = 2")
```

### 严格列表匹配

```python
orders = [
    {"orderId": "ORD-001", "status": "PAID"},
    {"orderId": "ORD-002", "status": "PENDING"}
]

expect(orders).should("""
    = [{
        orderId: 'ORD-001'
        status: PAID
    } {
        orderId: 'ORD-002'
        status: PENDING
    }]
""")
```

### 混合列表

```python
# 包含不同类型的列表
data = [1, "hello", 3.14, True, None]
expect(data).should("[1 'hello' 3.14 true null]")

# 包含对象的列表
data = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30}
]
expect(data).should("""
    [{
        name: Alice
        age: *
    } {
        name: Bob
        age: *
    }]
""")
```

## 表格验证

表格验证用于验证对象列表，支持排序、跳过、行标题等高级功能。

### 基础表格

```python
data = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

expect(data).should("""
    | id | name  |
    | 1  | Alice |
    | 2  | Bob   |
""")
```

### 严格表格

```python
# 使用 =| 表示严格模式，不允许有多余列
data = [{"id": 1, "name": "Alice"}]

expect(data).should("""
    =| id | name  |
    | 1  | Alice |
""")
```

### 表格排序

```python
data = [
    {"id": 3, "name": "C"},
    {"id": 1, "name": "A"},
    {"id": 2, "name": "B"}
]

# 升序排序
expect(data).should("""
    | id | name | sort by id asc |
    | 1  | A    |
    | 2  | B    |
    | 3  | C    |
""")

# 降序排序
expect(data).should("""
    | id | name | sort by id desc |
    | 3  | C    |
    | 2  | B    |
    | 1  | A    |
""")
```

### 跳过行

```python
data = [
    {"id": 1, "name": "First"},
    {"id": 2, "name": "Second"},
    {"id": 3, "name": "Third"},
    {"id": 4, "name": "Fourth"}
]

# 跳过前2行，验证后2行
expect(data).should("""
    | id | name   | skip 2 |
    | 3  | Third  |
    | 4  | Fourth |
""")
```

### 行标题

```python
data = [
    {"row_id": "row1", "value": 100},
    {"row_id": "row2", "value": 200}
]

# 第一列作为行标题（不参与验证）
expect(data).should("""
    | row_id | value | row header |
    | row1   | 100   |
    | row2   | 200   |
""")
```

### 表格转置

```python
data = [
    {"property": "name", "value": "Alice"},
    {"property": "age", "value": 25}
]

# 转置表格（行列互换）
expect(data).should("""
    | property | value | transpose |
    | name     | Alice |
    | age      | 25    |
""")
```

## 通配符

### 任意值 (*)

匹配任意非 null 值：

```python
expect("hello").should("*")
expect(123).should("*")
expect({"key": "value"}).should("*")

# 不匹配 null
# expect(None).should("*")  # 失败
```

### 任意对象 (**)

匹配任意对象（字典）：

```python
expect({"key": "value"}).should("**")
expect({}).should("**")
expect({"nested": {"key": "value"}}).should("**")

# 不匹配非对象
# expect("hello").should("**")  # 失败
# expect([1, 2, 3]).should("**")  # 失败
```

### 任意列表 (***)

匹配任意列表：

```python
expect([1, 2, 3]).should("***")
expect([]).should("***")
expect([{"key": "value"}]).should("***")

# 不匹配非列表
# expect("hello").should("***")  # 失败
# expect({"key": "value"}).should("***")  # 失败
```

### 通配符在对象中

```python
data = {"name": "张三", "value": 123}
expect(data).should("""
    : {
        name: *
        value: *
    }
""")
```

### 通配符在列表中

```python
data = [1, "hello", {"key": "value"}]
expect(data).should("[* * *]")
```

## 元数据访问

### 大小 (::size)

```python
# 字典大小
expect({"a": 1, "b": 2}).should("::size = 2")

# 列表大小
expect([1, 2, 3, 4, 5]).should("::size = 5")

# 字符串长度
expect("hello").should("::size = 5")
```

### 类型 (::type)

```python
expect({"key": "value"}).should("::type = dict")
expect([1, 2, 3]).should("::type = list")
expect("hello").should("::type = str")
expect(123).should("::type = int")
expect(1.5).should("::type = float")
```

### 键 (::keys)

```python
data = {"name": "张三", "age": 25}
expect(data).should("::keys")  # 返回 ["name", "age"]
expect(data).should("::size = 2")
```

### 根对象 (::root)

```python
data = {"user": {"name": "张三"}}
expect(data).should("user.name = '张三'")
expect(data).should("::root.user.name = '张三'")
```

### 当前对象 (::this)

```python
data = {"name": "张三"}
expect(data).should("::this.name = '张三'")

# 列表中使用
data = [1, 2, 3]
expect(data).should("::this[0] = 1")
```

### 公共键 (::common)

用于对象列表，返回所有对象的公共键：

```python
data = [
    {"name": "A", "age": 20},
    {"name": "B", "age": 25}
]
expect(data).should("::common")  # 返回 ["name", "age"]
```

## Schema 验证

### 内置 Schema

```python
from mangotools.dal import expect
from mangotools.dal.schema import validate_schema

# AlmostNow - 验证时间戳是否接近当前时间（±5秒）
from datetime import datetime
expect(datetime.now()).should("is AlmostNow")

# Instant - 验证是否为合法的时间戳格式
expect(1234567890).should("is Instant")
expect("2024-01-01T00:00:00Z").should("is Instant")

# NotEmpty - 验证非空
expect("hello").should("is NotEmpty")
expect([1, 2, 3]).should("is NotEmpty")

# NotNull - 验证非 null
expect("value").should("is NotNull")

# Positive - 验证正数
expect(5).should("is Positive")

# Negative - 验证负数
expect(-5).should("is Negative")

# ValidEmail - 验证邮箱格式
expect("test@example.com").should("is ValidEmail")

# ValidUUID - 验证 UUID 格式
expect("550e8400-e29b-41d4-a716-446655440000").should("is ValidUUID")

# ValidURL - 验证 URL 格式
expect("https://example.com").should("is ValidURL")

# ValidIP - 验证 IP 地址格式
expect("192.168.1.1").should("is ValidIP")

# String - 验证字符串
expect("hello").should("is String")

# Integer - 验证整数
expect(42).should("is Integer")

# Number - 验证数字
expect(3.14).should("is Number")

# Boolean - 验证布尔值
expect(True).should("is Boolean")
```

### Schema Which 子句

```python
# 条件 Schema 验证
data = {"type": "user", "name": "张三"}

expect(data).should("""
    : {
        type: 'user'
        name: is String which NotEmpty
    }
""")
```

### 自定义 Schema

```python
from mangotools.dal.schema import register_schema, SchemaValidationResult

# 注册自定义 Schema
@register_schema("EvenNumber")
def validate_even(value):
    if isinstance(value, int) and value % 2 == 0:
        return SchemaValidationResult(success=True)
    return SchemaValidationResult(
        success=False,
        message=f"Expected even number, got {value}"
    )

# 使用自定义 Schema
expect(4).should("is EvenNumber")
```

## 异步等待

### 基础用法

使用 `::eventually` 进行异步等待，轮询直到条件成立：

```python
import time
import threading
from mangotools.dal import expect

# 等待列表大小变为 5
data = []

def add_items():
    time.sleep(0.5)
    data.extend([1, 2, 3, 4, 5])

thread = threading.Thread(target=add_items)
thread.start()

try:
    expect(data).should("::eventually ::size = 5")
finally:
    thread.join()
```

### 等待对象属性

```python
data = {"status": "pending"}

def update_status():
    time.sleep(0.3)
    data["status"] = "completed"

thread = threading.Thread(target=update_status)
thread.start()

try:
    expect(data).should("::eventually status = 'completed'")
finally:
    thread.join()
```

### 等待嵌套属性

```python
data = {"user": {"name": "Alice", "active": False}}

def activate():
    time.sleep(0.3)
    data["user"]["active"] = True

thread = threading.Thread(target=activate)
thread.start()

try:
    expect(data).should("::eventually user.active = True")
finally:
    thread.join()
```

### 超时处理

默认超时时间为 5 秒，如果超时条件仍未成立会抛出 `AssertionError`：

```python
data = [1, 2]

# 这会在 5 秒后超时失败
try:
    expect(data).should("::eventually ::size = 5")
except AssertionError as e:
    print("Timeout:", e)
```

## 自定义操作符

### 注册自定义操作符

```python
from mangotools.dal.core.operators import Operators, CompareResult

# 注册自定义操作符
@Operators.register("~=")
def fuzzy_match(actual, expected):
    """模糊匹配操作符"""
    if isinstance(actual, str) and isinstance(expected, str):
        success = expected.lower() in actual.lower()
        return CompareResult(
            success=success,
            expected=f"contains '{expected}' (case insensitive)",
            actual=actual,
            message="" if success else f"'{actual}' does not contain '{expected}'"
        )
    return CompareResult(
        success=False,
        expected=f"string containing '{expected}'",
        actual=str(actual),
        message="Fuzzy match requires strings"
    )

# 使用自定义操作符
expect("Hello World").should("~= 'hello'")  # 通过
```

### 管理自定义操作符

```python
# 列出所有自定义操作符
print(Operators.list_custom())  # ['~=']

# 注销操作符
Operators.unregister("~=")

# 清除所有自定义操作符
Operators.clear_custom()
```

## pytest-bdd 集成

DAL 可以与 pytest-bdd 集成，在 Gherkin 特性文件中使用。

### 特性文件示例

创建 `test_dal.feature`：

```gherkin
Feature: DAL 数据验证

  Scenario: 验证对象数据
    Given 数据为:
      """
      {
        "name": "张三",
        "age": 25,
        "email": "zhangsan@example.com"
      }
      """
    When 使用 DAL 表达式验证 "name = '张三'"
    Then 验证通过

  Scenario: 验证列表数据
    Given 列表数据为:
      """
      [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
      ]
      """
    When 使用 DAL 表达式验证:
      """
      | id | name  |
      | 1  | Alice |
      | 2  | Bob   |
      """
    Then 验证通过
```

### Step Definitions

```python
# conftest.py
import json
import pytest
from pytest_bdd import given, when, then, parsers
from mangotools.dal import expect


class TestContext:
    def __init__(self):
        self.data = None
        self.expression = None
        self.last_result = None
        self.last_error = None


@pytest.fixture
def ctx():
    return TestContext()


@given(parsers.parse('数据为:'), target_fixture='test_data')
def given_data(ctx, docstring):
    ctx.data = json.loads(docstring)
    return ctx.data


@given(parsers.parse('列表数据为:'), target_fixture='list_data')
def given_list_data(ctx, docstring):
    ctx.data = json.loads(docstring)
    return ctx.data


@when(parsers.parse('使用 DAL 表达式验证 "{expression}"'))
def when_validate_expression(ctx, expression):
    ctx.expression = expression
    try:
        expect(ctx.data).should(expression)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@when(parsers.parse('使用 DAL 表达式验证:'))
def when_validate_multiline_expression(ctx, docstring):
    ctx.expression = docstring.strip()
    try:
        expect(ctx.data).should(docstring)
        ctx.last_result = True
        ctx.last_error = None
    except AssertionError as e:
        ctx.last_result = False
        ctx.last_error = str(e)


@then('验证通过')
def then_validation_passes(ctx):
    assert ctx.last_result is True, f"验证失败: {ctx.last_error}"


@then('验证失败')
def then_validation_fails(ctx):
    assert ctx.last_result is False, "预期验证失败，但实际通过了"
```

## 完整示例

### API 响应验证

```python
import requests
from mangotools.dal import expect

def test_api_response():
    response = requests.get("https://api.example.com/users/1")
    data = response.json()

    # 验证响应结构
    expect(data).should("""
        : {
            id: is Integer
            name: is String which NotEmpty
            email: is ValidEmail
            createdAt: is Instant
            status: 'active' or = 'inactive'
        }
    """)

    # 验证嵌套对象
    expect(data).should("""
        : {
            profile: **
            settings.notifications: true or = false
        }
    """)

    # 验证列表
    expect(data).should("roles.size >= 1")
    expect(data).should("""
        roles: [{
            id: is Integer
            name: is String
        } *]
    """)
```

### 数据库查询结果验证

```python
def test_database_query():
    # 模拟数据库查询结果
    orders = [
        {"orderId": "ORD-001", "amount": 100.0, "status": "PAID"},
        {"orderId": "ORD-002", "amount": 200.0, "status": "PENDING"},
        {"orderId": "ORD-003", "amount": 150.0, "status": "SHIPPED"}
    ]

    # 验证订单列表
    expect(orders).should("""
        | orderId   | amount | status   | sort by orderId asc |
        | ORD-001   | 100.0  | PAID     |
        | ORD-002   | 200.0  | PENDING  |
        | ORD-003   | 150.0  | SHIPPED  |
    """)

    # 验证金额范围
    for order in orders:
        expect(order).should("amount > 0 and amount < 1000")
```

### 异步任务验证

```python
import time
import threading
from mangotools.dal import expect

def test_async_task():
    task = {"id": 1, "status": "pending", "progress": 0}

    def process_task():
        time.sleep(0.5)
        task["status"] = "processing"
        time.sleep(0.5)
        task["progress"] = 50
        time.sleep(0.5)
        task["status"] = "completed"
        task["progress"] = 100

    thread = threading.Thread(target=process_task)
    thread.start()

    try:
        # 等待任务完成
        expect(task).should("::eventually status = 'completed'")
        expect(task).should("::eventually progress = 100")
    finally:
        thread.join()
```

## 最佳实践

1. **使用宽容匹配 (:) 进行灵活验证**
   ```python
   expect(data).should(": { name: '张三' }")  # 推荐
   ```

2. **使用严格匹配 (=) 进行精确验证**
   ```python
   expect(data).should("= { name: '张三' }")  # 不允许多余字段
   ```

3. **使用通配符 (*) 忽略不关心的值**
   ```python
   expect(data).should(": { id: *, name: '张三' }")
   ```

4. **使用 Schema 进行类型验证**
   ```python
   expect(data).should(": { email: is ValidEmail }")
   ```

5. **使用 ::eventually 处理异步场景**
   ```python
   expect(data).should("::eventually status = 'completed'")
   ```

6. **组合多个验证条件**
   ```python
   expect(data).should("> 0 and < 100 and != 50")
   ```

## 错误处理

当验证失败时，会抛出 `AssertionError` 并提供详细的错误信息：

```python
try:
    expect({"name": "李四"}).should("name = '张三'")
except AssertionError as e:
    print(e)
    # 输出: Expected '张三', got '李四' at path 'name'
```

## 许可证

MIT License
