# 智书合同 UI 自动化测试 — 开发指南

## 1. 架构概览

```
四层架构：

  Feature 文件（Gherkin 中文语法）
       │
  Step 步骤定义层（common / home / system）
       │
  Page Object 页面对象层（元素定位 + 操作封装）
       │
  Playwright（浏览器驱动）
```

目录结构：

```
auto_tests/qfei_contract_ui/
├── __init__.py              # 项目元数据
├── conftest.py              # pytest 配置（手动注册 steps）
├── config/                  # 多环境配置（同 API 项目）
│   ├── settings.py
│   ├── __init__.py
│   └── .env.dev/test/pre
├── steps/                   # 步骤定义
│   ├── common/              #   通用 fixture（driver, base_data）
│   ├── home/                #   首页步骤
│   └── system/              #   系统管理步骤
├── test_cases/              # Feature 文件 + BDD 绑定
│   ├── home/                #   首页测试
│   └── system/              #   系统管理测试
└── page_object/             # 页面对象封装
    ├── home.py
    └── system/
```

---

## 2. 快速开始

### 2.1 运行测试

```bash
# 单个测试
ENV=test .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_ui/test_cases/home/test_home_bdd.py -v

# 按模块
ENV=test .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_ui/test_cases/system/ -v
```

### 2.2 环境切换

UI 项目默认使用 `test` 环境（`DEFAULT_ENV = "test"`），切环境：

```bash
ENV=dev .venv/Scripts/python -m pytest auto_tests/qfei_contract_ui/... -v
```

---

## 3. Feature 文件编写

```gherkin
# language: zh-CN
功能: 合同字段管理

  场景: 添加合同字段
    当 我打开合同字段管理页面
    并且 我点击添加字段按钮
    并且 我输入字段名称
    并且 我选择字段类型为单行文本
    并且 我点击确认
    那么 我应该看到添加成功提示
```

---

## 4. Step 步骤定义编写

### 4.1 基本模式

```python
from typing import Any, Dict
from pytest_bdd import when, parsers

@when('我打开合同字段管理页面', target_fixture="page_context")
def open_contract_fields_page(
    base_data: Dict[str, Any],
    test_data: Dict[str, Any]
):
    from auto_tests.qfei_contract_ui.page_object.system.contract_fields import \
        ContractFieldsPage

    page = ContractFieldsPage(base_data, test_data)
    page.goto()
    return {"page": page}
```

### 4.2 Fixture 清单

| Fixture | 作用域 | 说明 |
|---------|--------|------|
| `driver_object` | function | Playwright 浏览器实例 |
| `base_data` | function | 浏览器底层操作封装 |
| `test_data` | function | 测试数据生成器 |
| `page_context` | function | 步骤间传递页面对象 |
| `ui_config` | session | UI 测试配置 |

### 4.3 跨步骤传递页面对象

```python
# Step 1: 打开页面
@when('打开XX页面', target_fixture="page_context")
def open_page(base_data, test_data):
    page = XXPage(base_data, test_data)
    page.goto()
    return {"page": page}

# Step 2: 在页面上操作
@when('点击新建按钮')
def click_create(page_context):
    page = page_context["page"]
    page.click_create()
```

---

## 5. Page Object 页面对象

### 5.1 基本模式

```python
from urllib.parse import urljoin
from auto_tests.qfei_contract_ui import PROJECT_NAME
from auto_tests.qfei_contract_ui.config import settings
from core.ui import WebBaseObject

class ContractFieldsPage(WebBaseObject):

    def __init__(self, base_data, test_data):
        super().__init__(
            PROJECT_NAME,                          # 项目名
            "系统管理",                             # 模块名
            "合同字段管理",                          # 页面名
            base_data,
            test_data,
        )
        self.url = urljoin(settings.BASE_URL, "/admin/contract-config/attributes")

    def goto(self):
        """打开页面"""
        self.w_goto(self.url)

    def create_field(self, name: str = None):
        """创建字段"""
        if name is None:
            name = "AUTO_" + self.test_data.str_random_string()
        self.test_data.set_cache("字段名称", name)
        self.w_click(self.element("添加字段"))
        self.w_input(self.element("添加字段-字段名称"), name)
        self.w_click(self.element("添加字段-字段类型"))
        self.w_click(self.element("添加字段-字段类型-单行文本"))
        self.w_click(self.element("添加字段-确认"))
        self.web_ass.a_assert_ele_exists(self.element("添加成功提示"))
        return name
```

### 5.2 关键方法

| 方法 | 说明 |
|------|------|
| `self.w_goto(url)` | 导航到指定 URL |
| `self.w_click(element)` | 点击元素 |
| `self.w_input(element, text)` | 输入文本 |
| `self.element("名称")` | 获取元素定位器 |
| `self.web_ass.a_assert_ele_exists(element)` | 断言元素存在 |
| `self.test_data.str_random_string()` | 生成随机字符串 |
| `self.test_data.set_cache(key, value)` | 缓存测试数据 |

### 5.3 目录规范

```
page_object/
├── home.py                    # 首页
└── system/                    # 系统管理
    ├── contract_fields.py     #   合同字段管理
    ├── contract_process.py    #   合同流程管理
    └── contract_type.py       #   合同类型管理
```

每个页面一个 Python 文件，类名以 `Page` 结尾。

---

## 6. 如何新增一个页面测试（完整示例）

### 6.1 创建 Page Object

`page_object/system/label_management.py`：

```python
from urllib.parse import urljoin
from auto_tests.qfei_contract_ui import PROJECT_NAME
from auto_tests.qfei_contract_ui.config import settings
from core.ui import WebBaseObject

class LabelManagementPage(WebBaseObject):

    def __init__(self, base_data, test_data):
        super().__init__(PROJECT_NAME, "系统管理", "标签管理", base_data, test_data)
        self.url = urljoin(settings.BASE_URL, "/admin/label-management")

    def goto(self):
        self.w_goto(self.url)

    def create_label(self, name: str = None):
        if name is None:
            name = "AUTO_" + self.test_data.str_random_string()
        self.w_click(self.element("添加标签"))
        self.w_input(self.element("标签名称输入框"), name)
        self.w_click(self.element("确认按钮"))
        return name
```

### 6.2 创建步骤定义

`steps/system/label_steps.py`：

```python
from typing import Any, Dict
from pytest_bdd import when, parsers

@when('我打开标签管理页面', target_fixture="page_context")
def open_label_page(base_data: Dict[str, Any], test_data: Dict[str, Any]):
    from auto_tests.qfei_contract_ui.page_object.system.label_management import \
        LabelManagementPage
    page = LabelManagementPage(base_data, test_data)
    page.goto()
    return {"page": page}

@when('我创建一个标签')
def create_label(page_context: Dict[str, Any]):
    page = page_context["page"]
    page.create_label()
```

### 6.3 创建 Feature 文件

`test_cases/system/label_management/label_management.feature`：

```gherkin
# language: zh-CN
功能: 标签管理

  场景: 创建标签
    当 我打开标签管理页面
    当 我创建一个标签
    那么 我应该看到标签创建成功提示
```

### 6.4 创建 BDD 绑定

`test_cases/system/label_management/test_label_management_bdd.py`：

```python
import allure
from pytest_bdd import scenario

@allure.title("创建标签")
@scenario("./label_management.feature", "创建标签")
def test_创建标签():
    pass
```

### 6.5 注册步骤

在 `conftest.py` 的 `pytest_plugins` 中添加：
```python
"auto_tests.qfei_contract_ui.steps.system.label_steps",
```

### 6.6 运行

```bash
ENV=test .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_ui/test_cases/system/label_management/ -v
```

---

## 7. API 项目与 UI 项目对比

| | API (qfei_contract_api) | UI (qfei_contract_ui) |
|---|---|---|
| 驱动方式 | HTTP 请求（httpx） | 浏览器（Playwright） |
| 认证方式 | Cookie / Bearer Token | 浏览器登录态 |
| Step 输出 | `api_response` | `page_context` |
| 状态共享 | 模块级 dict | `page_context["page"]` |
| 步骤注册 | 自动发现 | 手动 conftest.py |
| 默认环境 | `dev` | `test` |
| 测试标签 | pytest.ini 统一管理 | 同 |

---

## 8. 故障排查

**浏览器驱动启动失败？**
- 确认已安装浏览器（Chrome/Edge）
- 检查 Playwright 是否正确安装：`.venv/Scripts/playwright install chromium`

**元素定位失败？**
- 检查页面 URL 是否正确
- 使用 `base_data.wait_for_selector()` 等待元素出现
- 确认元素名称在 Page Object 中正确定义

**点击/输入操作没反应？**
- 添加显式等待：`self.base_data.wait_for_element(element)`
- 检查是否有遮罩层（弹窗）阻挡
- 确认元素处于可交互状态
