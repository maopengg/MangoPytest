# Steps — 步骤定义层设计

## 职责

将 Gherkin 步骤文本映射为 Python 函数，连接 Feature 文件和 Page Object。

## 设计思路

```
Feature: 当 用户进入元素点击页面
    ↓
def user_enter_click_page(logged_in_user, page_context):
    home = page_context.get("首页") or HomePage(...)
    home.goto()
    click_page = ClickPage(...)
    page_context["点击"] = click_page
```

## 目录结构

```
steps/
├── common/           # 公共（fixture 已迁移到 fixtures/）
├── home/             # 首页相关步骤
│   └── home_steps.py
├── click_steps.py    # 元素点击步骤
├── alert_steps.py    # 弹窗步骤
└── ...
```

## 写法

### 页面进入步骤

```python
from pytest_bdd import when
from auto_tests.<project>.page_object.home import HomePage
from auto_tests.<project>.page_object.click import ClickPage


@when("用户进入元素点击页面")
def user_enter_click_page(logged_in_user, page_context):
    # 确保首页已加载
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home

    # 创建目标页面对象
    click_page = ClickPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["点击"] = click_page
```

### 页面操作步骤

```python
@when("用户执行双击操作")
def user_perform_double_click(logged_in_user, page_context, test_data_context):
    click_page = page_context["点击"]
    result = click_page.test_double_click()
    test_data_context["双击结果"] = result   # 传递结果给后续断言
```

### 断言步骤

```python
@then("双击操作应该成功")
def verify_double_click_success(test_data_context):
    assert test_data_context.get("双击结果") is not None, "双击操作失败"
```

## 步骤间数据传递

```
@when 步骤 → test_data_context["结果"] = value
@then 步骤 → assert test_data_context.get("结果")

@when 步骤 → page_context["页面名"] = page_object
后续步骤 → page_context.get("页面名")
```

两个 dict fixture 实现步骤间解耦：

| fixture | 用途 | 示例 key |
|---------|------|---------|
| `page_context` | 共享 Page Object | `"首页"`, `"点击"` |
| `test_data_context` | 共享业务数据 | `"双击结果"`, `"输入结果"` |

## 新增步骤

1. 在 `steps/` 下新建 `.py` 文件
2. conftest 自动发现，无需手动注册
3. 如果步骤属于特定模块，可以建子目录
