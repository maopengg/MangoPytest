# DAL 断言指南

DAL（Data Assertion Language）是一套数据断言引擎，提供近似 JSON 的轻量语法来统一描述断言目标。所有断言通过 `expect(data).should(expression)` 执行，一条表达式描述完整的数据期望。

---

## 一、架构

```
Feature 文件                    步骤定义                       DAL 引擎
───────────                    ────────                       ───────
那么 响应应该为:    →  api_response 展平为        →  expect(data).should(expr)
  \"\"\"                     {status_code, body}
  status_code = 200
  body.code = 200
  \"\"\"

那么 "name"应该为"张三" →  拼装 DAL 表达式             →  expect(data).should("name = '张三'")

那么 数据应该匹配:    →  直接传入 DAL                →  expect(data).should(docstring)
  \"\"\"
  name = 张三
  \"\"\"
```

---

## 二、步骤速查

### 2.1 主入口（TestCharm 风格）

| 步骤 | 用途 | 示例 |
|------|------|------|
| `那么 响应应该为:` | API 响应统一断言，展平为 `{status_code, body}` 后执行 DAL | 见下方 |
| `那么 响应体应该为:` | 直接对 body 执行 DAL（跳过 status_code） | `那么 响应体应该为:` |
| `那么 数据应该匹配:` | 通用 DAL 多行断言，操作 `data` fixture | `那么 数据应该匹配:` |
| `那么 数据应该匹配表格:` | DAL 表格断言 | `那么 数据应该匹配表格:` |

### 2.2 API 响应便捷步骤

| 步骤 | Feature 写法 |
|------|-------------|
| 状态码 | `那么 响应状态码应该为200` |
| 单字段 | `那么 响应字段"code"应该为"200"` |
| 消息包含 | `那么 响应消息应该包含"成功"` |

### 2.3 紧凑路径断言（操作 data fixture）

| 步骤 | 写法 |
|------|------|
| 字符串等值 | `那么 "name"应该为"张三"` |
| 整数等值 | `那么 "age"应该为25` |
| 布尔 true | `那么 "active"应该为true` |
| 布尔 false | `那么 "deleted"应该为false` |
| 字段存在 | `那么 "address"应该存在` |
| 大小等于 | `那么 "items"大小应该为3` |
| 大小大于 | `那么 "items"大小应该大于0` |
| 大于 | `那么 "age"应该大于18` |
| 包含 | `那么 "tags"应该包含"VIP"` |
| 正则匹配 | `那么 "zip"应该匹配"\d{6}"` |
| 不为空 | `那么 "items"不应该为空` |
| 列表长度 | `那么 列表长度应该为5` |
| 列表长度 >= | `那么 列表长度应该大于等于1` |
| 异步等待 | `那么 最终"status"应该为"completed"` |

---

## 三、DAL 表达式语法

### 3.1 操作符

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `=` | 严格相等（类型 + 值） | `status_code = 200` |
| `:` | 宽容匹配（值相等即可） | `: { name: 张三 }` |
| `!=` | 不等于 | `status != deleted` |
| `>` | 大于 | `score > 60` |
| `<` | 小于 | `age < 100` |
| `>=` | 大于等于 | `size >= 1` |
| `<=` | 小于等于 | `price <= 100` |
| `and` | 逻辑与 | `score > 60 and score < 90` |
| `or` | 逻辑或 | `status = active or status = pending` |
| `not` | 逻辑非 | `not (status = deleted)` |
| `contains` | 字符串/列表包含 | `message contains 成功` |
| `starts` | 字符串开头匹配 | `code starts ORD` |
| `ends` | 字符串结尾匹配 | `email ends @example.com` |
| `/regex/` | 正则匹配 | `orderId = /ORD-\d+/` |

### 3.2 路径访问

| 语法 | 含义 | 示例 |
|------|------|------|
| `.property` | 对象属性 | `body.code` |
| `[index]` | 数组索引 | `data[0].name` |
| `::size` | 元数据：大小 | `items.size ::size` |
| `::type` | 元数据：类型 | `::type` |
| `is NotNull` | 字段非空 | `address is NotNull` |
| `is ValidEmail` | Schema 验证 | `email is ValidEmail` |
| `root` | 根数据 | `root` |

### 3.3 字面量

| 类型 | 写法 |
|------|------|
| 数字 | `200`, `1.5`, `-10` |
| 字符串（引号） | `'张三'`, `"hello"` |
| 字符串（裸标识符） | `张三`, `active` — 找不到属性时自动当作字符串 |
| 布尔 | `true`, `false` |
| 空 | `null` |
| 正则 | `/ORD-\d+/` |

### 3.4 `=` vs `:` — 严格 vs 宽容

```
# 宽容模式：只验证写出来的字段，其余忽略
: { name: 张三, id: 1 }
  实际: {"name": "张三", "id": 1, "extra": "x"} → 通过

# 严格模式：不能有多余字段
= { name: 张三, id: 1 }
  实际: {"name": "张三", "id": 1, "extra": "x"} → 失败（多余字段 extra）
```

### 3.5 对象断言

```
# 单行
: { name: 张三, age: 25 }

# 多行（推荐）
: {
  name: 张三
  age: 25
  address.city: 北京
}

# 字段存在性
: {
  name: *        # name 必须存在，值任意
  phone?:        # phone 可选
}
```

### 3.6 表格断言

```
# 宽容表格
那么 数据应该匹配表格:
  """
  | id | name |
  | 1  | 张三 |
  | 2  | 李四 |
  """

# 严格表格（行数精确匹配）
那么 数据应该匹配:
  """
  = | id | name |
    | 1  | 张三 |
    | 2  | 李四 |
  """

# 表格选项
| id | name | sort by id asc |   # 按 id 升序
| id | name | skip 1 |           # 跳过第1行
| id | name | row header |       # 第一列为行标题
```

### 3.7 异步等待

```
# 轮询等待 status 变为 completed（默认 5s 超时，0.5s 间隔）
那么 数据应该匹配:
  """
  ::eventually status = completed
  """
```

---

## 四、Feature 文件示例

### 4.1 简单 GET 验证

```gherkin
场景: 获取合同主页弹窗
  当 GET "/clm/api/tipNotice/homePage"
  那么 响应应该为:
    """
    status_code = 200
    body.code = 200
    body.success = true
    """
```

### 4.2 带列表验证

```gherkin
场景: 查询所有币种信息
  当 GET "/clm/api/currency/findAll"
  那么 响应应该为:
    """
    status_code = 200
    body.code = 200
    body.data.size > 0
    body.data[0].currencyId: *
    """
```

### 4.3 POST 带请求体

```gherkin
场景: 获取履约监控列表
  当 POST "/clm/api/myContractReminder/list":
    """
    {
      "contractReminderTypeCode": "",
      "reminderStartDate": 1751904000000,
      "reminderEndDate": 1909065599999
    }
    """
  那么 响应应该为:
    """
    status_code = 200
    body.code = 200
    """
```

### 4.4 路径断言风格

```gherkin
场景: 用户详情验证
  背景:
    假如 准备数据:
      """
      {"name": "张三", "age": 25, "address": {"city": "北京"}, "tags": ["VIP"]}
      """

  那么 "name"应该为"张三"
  那么 "age"应该大于18
  那么 "address.city"应该为"北京"
  那么 "tags"大小应该为1
  那么 "name"应该存在
  那么 "tags"应该包含"VIP"
```

### 4.5 通用数据断言

```gherkin
场景: 复杂数据验证
  假如 准备数据:
    """
    {"user": {"name": "张三", "role": "admin"}, "permissions": ["read", "write"]}
    """
  那么 数据应该匹配:
    """
    user.name = 张三
    user.role = admin
    permissions.size = 2
    permissions[0] = read
    """
```

### 4.6 严格对象 + 正则

```gherkin
场景: 订单数据精确验证
  假如 准备数据:
    """
    {"orderId": "ORD-2024-001", "status": "PAID"}
    """
  那么 数据应该匹配:
    """
    = { orderId: /ORD-\d{4}-\d{3}/, status: PAID }
    """
```

---

## 五、内置 Schema 验证器

| Schema | 验证内容 |
|--------|---------|
| `NotNull` | 值不为 null |
| `NotEmpty` | 字符串/列表/字典不为空 |
| `String` | 字符串类型 |
| `Number` | 数字类型 |
| `Integer` | 整数类型 |
| `Boolean` | 布尔类型 |
| `Array` | 列表类型 |
| `Object` | 字典类型 |
| `Positive` | 正数 |
| `Negative` | 负数 |
| `NonNegative` | 非负数 |
| `ValidEmail` | 合法邮箱格式 |
| `ValidURL` | 合法 URL 格式 |
| `ValidUUID` | 合法 UUID 格式 |
| `AlmostNow` | 时间戳接近当前时间（±5s） |
| `Instant` | 合法时间戳格式 |

用法：
```
email is ValidEmail
createdAt is Instant
age is Positive
```

---

## 六、自定义操作符

```python
from core.dal import Operators, CompareResult

@Operators.register("has")
def has_match(actual, expected):
    """检查 actual 是否包含 expected"""
    if isinstance(actual, str) and isinstance(expected, str):
        ok = expected in actual
        return CompareResult(success=ok, expected=f"has '{expected}'", actual=str(actual))
    return CompareResult(success=False, expected=f"string", actual=str(actual))

# 使用: message has 成功
```

