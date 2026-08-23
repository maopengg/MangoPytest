# Test Cases — Feature 文件与 BDD 绑定

## 职责

测试用例层，每个模块一个子目录，包含 `.feature` 文件和中转绑定脚本。

## 目录结构

```
test_cases/
├── user/
│   ├── user.feature          # Gherkin 场景
│   └── test_user_bdd.py      # @scenario 绑定
├── order/
│   ├── order.feature
│   └── test_order_bdd.py
└── ...
```

每个业务模块一个子目录，内部一对 `.feature` + `test_*_bdd.py`。

---

## 测试分层

用例设计遵循三层金字塔，详见 [测试分层](../用例设计.md)。

```
API (60%) → Integration (30%) → E2E (10%)
```

Feature 文件对应三层分别用 `@smoke/@positive/@negative`、`@integration`、`@e2e` 标签区分。

---

## Feature 文件格式

### 语法要点

| Gherkin | 对应步骤 | 说明 |
|---------|---------|------|
| `# language: zh-CN` | — | 声明中文语法 |
| `功能: xxx` | — | 模块名称 |
| `背景:` | `@given` | 每个场景执行前先跑 |
| `场景: xxx` | — | 一个测试函数 |
| `@smoke @positive` | markers | 标签过滤 |
| `假如 ...` | `@given` | 前置条件 |
| `当 ...` | `@when` | 操作 |
| `那么 ...` | `@then` | 断言 |
| `而且 ...` | 同上一步 | 连接词 |

### 背景（Background）

```gherkin
背景:
  假如 管理员已登录
```

### JSON 数据体

步骤中的 JSON 字符串支持 `${变量}` 占位符：

```gherkin
当 使用用户ID PUT "/users/${user.id}":
"""
{
  "username": "AUTO_updated_${user.id}",
  "email": "new@example.com"
}
"""
```

### BDD 绑定文件

```python
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("用户管理"),
    allure.feature("用户CRUD"),
    allure.story("基本操作"),
]

scenarios("user.feature")
```

`scenarios("user.feature")` 自动把 feature 文件里所有场景注册为 pytest 测试函数。

单场景绑定时用 `@scenario`：

```python
from pytest_bdd import scenario

@scenario("user.feature", "创建新用户")
def test_create_user():
    pass
```
