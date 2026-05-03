# MangoPytest UI 测试项目重构方案

## 一、设计理念

MangoPytest 是多项目 API+UI 自动化 demo。UI 部分改为两个范式独立项目，参照 qfei_contract_ui 的成熟模式。

### 核心原则

1. **每个项目自包含** — page_object、config、fixtures/steps 都在各自项目内，不跨项目共享
2. **参照成熟范式** — BDD UI 完全参照 `qfei_contract_ui`；pytest UI 保持独立范式
3. **零向后兼容负担** — 这是 demo，直接做最干净的设计

---

## 二、目标架构

```
auto_tests/
├── api_mock/              # [保持] 经典 pytest API
├── bdd_api_mock/          # [保持] BDD API（五层架构）
├── pytest_api_mock/       # [保持] pytest API（五层架构 + Builder 模式）
├── pytest_ui_mock/        # [改造] ui_mock 重命名，改造 page_object 构造函数
└── bdd_ui_mock/           # [新建] BDD UI，完全参照 qfei_contract_ui
```

### 命名规则

| 项目名 | 范式 | 类型 | 来源 |
|--------|------|------|------|
| `pytest_ui_mock` | pytest | UI | `ui_mock` 重命名 |
| `bdd_ui_mock` | BDD | UI | 新建，参照 `qfei_contract_ui` |

---

## 三、pytest_ui_mock（ui_mock 重命名 + 改造）

### 3.1 变更清单

| # | 操作 |
|---|------|
| 1 | `ui_mock/` → `pytest_ui_mock/` |
| 2 | `abstract/` → `page_object/` |
| 3 | Page Object 构造函数改写为 qfei_contract_ui 模式（PROJECT_NAME + urljoin） |
| 4 | 全量替换导入路径 `auto_tests.ui_mock` → `auto_tests.pytest_ui_mock` |
| 5 | 更新 `__init__.py`：PROJECT_NAME = `"pytest_ui_mock"` |
| 6 | 更新 `config/settings.py`：类名 `MockUIConfig` → `PytestUIMockConfig` |
| 7 | 新增 `pytest.ini` |
| 8 | 删除 `__pycache__` |

### 3.2 目标结构

```
auto_tests/pytest_ui_mock/
├── __init__.py               # PROJECT_NAME + 通知配置
├── conftest.py               # from fixtures.conftest import *
├── pytest.ini
├── config/
│   ├── __init__.py
│   ├── settings.py           # PytestUIMockConfig
│   └── .env.dev/test/pre/prod
├── page_object/              # [rename from abstract/] 扁平
│   ├── __init__.py
│   ├── home.py               # HomePage
│   ├── alert.py              # AlertPage
│   ├── batch.py              # BatchPage
│   ├── click.py              # ClickPage
│   ├── flash.py              # FlashPage
│   ├── iframe.py             # IframePage
│   ├── input.py              # InputPage
│   ├── keyboard.py           # KeyboardPage
│   ├── mouse.py              # MousePage
│   ├── navigation.py         # NavigationPage
│   ├── scroll.py             # ScrollPage
│   └── upload.py             # UploadPage
├── fixtures/
│   ├── __init__.py
│   ├── conftest.py
│   └── infra/
│       ├── __init__.py
│       ├── client.py         # driver_object (session)
│       └── base_data.py      # base_data (function)
├── test_cases/               # 扁平
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_alert.py
│   ├── test_batch.py
│   ├── test_click.py
│   ├── test_flash.py
│   ├── test_iframe.py
│   ├── test_input.py
│   ├── test_keyboard.py
│   ├── test_mouse.py
│   ├── test_navigation.py
│   ├── test_scroll.py
│   └── test_upload.py
├── scripts/
│   └── __init__.py
└── upload/
    └── 测试上传文件UI.xlsx
```

### 3.3 Page Object 改造

所有 Page Object 统一为 qfei_contract_ui 模式：

```python
# page_object/home.py
from urllib.parse import urljoin

from mangoautomation.uidrive import BaseData

from auto_tests.pytest_ui_mock import PROJECT_NAME
from auto_tests.pytest_ui_mock.config import settings
from core.ui import WebBaseObject
from core.utils.obtain_test_data import ObtainTestData


class HomePage(WebBaseObject):

    def __init__(self, base_data: BaseData, test_data: ObtainTestData):
        project_name = PROJECT_NAME
        module_name = "模拟首页"
        page_name = "首页"
        url_path = "/"
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(settings.BASE_URL, url_path)

    def goto(self):
        self.w_goto(self.url)
```

### 3.4 test_cases 示例

```python
# test_cases/test_click.py
import allure
from auto_tests.pytest_ui_mock.page_object.home import HomePage
from auto_tests.pytest_ui_mock.page_object.click import ClickPage
from core.utils.obtain_test_data import ObtainTestData


@allure.epic("Pytest UI Mock")
@allure.feature("元素点击")
class TestClick:
    test_data: ObtainTestData = ObtainTestData()

    @allure.story("双击")
    def test_double_click(self, base_data):
        home = HomePage(base_data, self.test_data)
        home.goto()
        click = ClickPage(base_data, self.test_data)
        result = click.test_double_click()
        assert result is not None
```

---

## 四、bdd_ui_mock（新建，参照 qfei_contract_ui）

### 4.1 定位

纯粹的 BDD UI 测试项目。有自己的 page_object（从 pytest_ui_mock 复制 + 微调导入路径），有 steps + test_cases。

### 4.2 五层架构

```
L5: test_cases/    → Feature 文件（Gherkin 中文） + BDD 绑定
L4: steps/         → @given / @when / @then 步骤定义
L3: page_object/   → WebBaseObject 子类（项目内自包含）
L2: core/ui        → WebBaseObject（框架层）
L1: mangoautomation → Playwright 浏览器驱动
```

### 4.3 目标结构

```
auto_tests/bdd_ui_mock/
├── __init__.py               # PROJECT_NAME="bdd_ui_mock" + 通知配置
├── conftest.py               # pytest_plugins + ui_config fixture
├── pytest.ini                # markers 定义
├── config/                   # [copy from pytest_ui_mock]
│   ├── __init__.py
│   ├── settings.py           # BddUIMockConfig
│   └── .env.dev/test/pre/prod
├── page_object/              # [copy from pytest_ui_mock, 改导入]
│   ├── __init__.py
│   ├── home.py
│   ├── alert.py
│   ├── batch.py
│   ├── click.py
│   ├── flash.py
│   ├── iframe.py
│   ├── input.py
│   ├── keyboard.py
│   ├── mouse.py
│   ├── navigation.py
│   ├── scroll.py
│   └── upload.py
├── steps/                    # BDD 步骤定义
│   ├── __init__.py
│   ├── common/
│   │   └── __init__.py       # driver_object, base_data, page_context, test_data_context, logged_in_user
│   ├── home/
│   │   ├── __init__.py
│   │   └── home_steps.py
│   ├── alert_steps.py
│   ├── batch_steps.py
│   ├── click_steps.py
│   ├── flash_steps.py
│   ├── iframe_steps.py
│   ├── input_steps.py
│   ├── keyboard_steps.py
│   ├── mouse_steps.py
│   ├── navigation_steps.py
│   ├── scroll_steps.py
│   └── upload_steps.py
├── test_cases/               # Feature 文件 + BDD 绑定（按模块子目录）
│   ├── __init__.py
│   ├── home/
│   │   ├── home.feature
│   │   └── test_home_bdd.py
│   ├── alert/
│   │   ├── alert.feature
│   │   └── test_alert_bdd.py
│   ├── batch/
│   │   ├── batch.feature
│   │   └── test_batch_bdd.py
│   ├── click/
│   │   ├── click.feature
│   │   └── test_click_bdd.py
│   ├── flash/
│   │   ├── flash.feature
│   │   └── test_flash_bdd.py
│   ├── iframe/
│   │   ├── iframe.feature
│   │   └── test_iframe_bdd.py
│   ├── input/
│   │   ├── input.feature
│   │   └── test_input_bdd.py
│   ├── keyboard/
│   │   ├── keyboard.feature
│   │   └── test_keyboard_bdd.py
│   ├── mouse/
│   │   ├── mouse.feature
│   │   └── test_mouse_bdd.py
│   ├── navigation/
│   │   ├── navigation.feature
│   │   └── test_navigation_bdd.py
│   ├── scroll/
│   │   ├── scroll.feature
│   │   └── test_scroll_bdd.py
│   └── upload/
│       ├── upload.feature
│       └── test_upload_bdd.py
├── data_factory/
│   ├── __init__.py
│   └── actions/
│       ├── __init__.py
│       └── composite_actions.py
├── scripts/
│   └── __init__.py
└── upload/
    └── 测试上传文件UI.xlsx
```

### 4.4 `__init__.py`

```python
# -*- coding: utf-8 -*-
"""bdd_ui_mock — BDD 范式 UI 自动化测试"""
from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum

PROJECT_NAME = "bdd_ui_mock"
PROJECT_TYPE = AutoTestTypeEnum.UI
DEFAULT_ENV = EnvironmentEnum.PRO
PROJECT_DISPLAY_NAME = "BDD UI Mock"

NOTICE_CHANNEL = "email"
NOTICE_EMAIL_SEND_LIST = ["729164035@qq.com"]
NOTICE_WECHAT_WEBHOOK = ""
NOTICE_FEISHU_WEBHOOK = ""
```

### 4.5 `conftest.py`

```python
# -*- coding: utf-8 -*-
"""bdd_ui_mock Pytest 配置"""
import pytest

pytest_plugins = [
    "auto_tests.bdd_ui_mock.steps.common",
    "auto_tests.bdd_ui_mock.steps.home.home_steps",
    "auto_tests.bdd_ui_mock.steps.alert_steps",
    "auto_tests.bdd_ui_mock.steps.batch_steps",
    "auto_tests.bdd_ui_mock.steps.click_steps",
    "auto_tests.bdd_ui_mock.steps.flash_steps",
    "auto_tests.bdd_ui_mock.steps.iframe_steps",
    "auto_tests.bdd_ui_mock.steps.input_steps",
    "auto_tests.bdd_ui_mock.steps.keyboard_steps",
    "auto_tests.bdd_ui_mock.steps.mouse_steps",
    "auto_tests.bdd_ui_mock.steps.navigation_steps",
    "auto_tests.bdd_ui_mock.steps.scroll_steps",
    "auto_tests.bdd_ui_mock.steps.upload_steps",
]


@pytest.fixture(scope="session")
def ui_config():
    from auto_tests.bdd_ui_mock.config import settings
    return settings
```

### 4.6 `steps/common/__init__.py`

```python
# -*- coding: utf-8 -*-
"""BDD UI Mock 公共 Fixtures — 参照 qfei_contract_ui/steps/common/__init__.py"""
import pytest
from mangoautomation.uidrive import DriverObject
from mangoautomation.uidrives import BaseData as BaseDataDrives

from core.enums.ui_enum import BrowserTypeEnum
from core.utils import log, project_dir
from core.utils.obtain_test_data import ObtainTestData


@pytest.fixture(scope="session")
def driver_object():
    driver = DriverObject(log)
    driver.set_web(web_type=BrowserTypeEnum.CHROMIUM.value, web_max=True)
    yield driver
    try:
        driver.web.close()
    except Exception:
        pass


@pytest.fixture(scope="function")
def base_data(driver_object):
    context, page = driver_object.web.new_web_page()
    test_data = ObtainTestData()
    base_data_obj = BaseDataDrives(test_data, log)
    base_data_obj.set_page_context(page, context)
    base_data_obj.set_file_path(project_dir.download(), project_dir.screenshot())
    yield base_data_obj
    try:
        context.close()
        page.close()
    except Exception as e:
        log.debug(f"清理页面上下文时出错: {e}")


@pytest.fixture
def page_context():
    """步骤间传递 Page Object 实例"""
    return {}


@pytest.fixture
def test_data_context():
    """步骤间传递业务数据"""
    return {}


@pytest.fixture
def logged_in_user(base_data):
    """BDD 步骤统一入口"""
    return {"base_data": base_data}
```

### 4.7 Step 定义示例（`steps/click_steps.py`）

```python
# -*- coding: utf-8 -*-
"""元素点击 BDD 步骤定义"""
from pytest_bdd import given, when, then

from auto_tests.bdd_ui_mock.page_object.home import HomePage
from auto_tests.bdd_ui_mock.page_object.click import ClickPage


@given("用户访问 Mock 首页")
def user_visit_mock_home(logged_in_user, page_context):
    home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    home.goto()
    page_context["首页"] = home


@when("用户进入元素点击页面")
def user_enter_click_page(logged_in_user, page_context):
    home = page_context.get("首页")
    if not home:
        home = HomePage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
        home.goto()
        page_context["首页"] = home
    home.switch_menu()
    click_page = ClickPage(logged_in_user["base_data"], logged_in_user["base_data"].test_data)
    page_context["点击"] = click_page


@when("用户执行双击操作")
def user_perform_double_click(logged_in_user, page_context, test_data_context):
    click_page = page_context["点击"]
    result = click_page.test_double_click()
    test_data_context["双击结果"] = result


@then("双击操作应该成功")
def verify_double_click_success(test_data_context):
    assert test_data_context.get("双击结果") is not None
```

### 4.8 Feature 文件示例（`test_cases/click/click.feature`）

```gherkin
# language: zh-CN
功能: 元素点击操作

  背景:
    假如 用户访问 Mock 首页

  @smoke @ui @positive
  场景: 双击元素
    当 用户进入元素点击页面
    而且 用户执行双击操作
    那么 双击操作应该成功

  @ui @positive
  场景: 右键点击元素
    当 用户进入元素点击页面
    而且 用户执行右键点击操作
    那么 右键点击操作应该成功

  @ui @positive
  场景: 强制点击元素
    当 用户进入元素点击页面
    而且 用户执行强制点击操作
    那么 强制点击操作应该成功

  @ui @positive
  场景: 普通点击元素
    当 用户进入元素点击页面
    而且 用户执行普通点击操作
    那么 普通点击操作应该成功

  @ui @positive
  场景: 悬停元素
    当 用户进入元素点击页面
    而且 用户执行悬停操作
    那么 悬停操作应该成功
```

### 4.9 BDD 绑定文件（`test_cases/click/test_click_bdd.py`）

```python
# -*- coding: utf-8 -*-
"""元素点击 BDD 测试绑定"""
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("元素点击"),
    allure.story("点击操作验证"),
]

scenarios("click.feature")
```

---

## 五、与 qfei_contract_ui 的对照

| 要素 | qfei_contract_ui | pytest_ui_mock | bdd_ui_mock |
|------|-----------------|---------------|-------------|
| Page Object | 项目内 `page_object/` | 项目内 `page_object/` | 项目内 `page_object/` |
| Config | 项目内 `config/` | 项目内 `config/` | 项目内 `config/` |
| project_name | PROJECT_NAME | PROJECT_NAME | PROJECT_NAME |
| 测试写法 | `.feature` + scenarios | `class TestXxx:` + pytest | `.feature` + scenarios |
| Steps | `steps/common/` + `steps/<domain>/` | 无 | `steps/common/` + `steps/<feature>_steps.py` |
| test_cases | `<domain>/` 子目录 | 扁平 | `<domain>/` 子目录 |
| conftest.py | pytest_plugins | fixtures 导入 | pytest_plugins |
| data_factory | `data_factory/actions/` | 无 | `data_factory/actions/` |

---

## 六、实施步骤

### 阶段 1：pytest_ui_mock 改造

| # | 操作 |
|---|------|
| 1 | `ui_mock/` → `pytest_ui_mock/` |
| 2 | `abstract/` → `page_object/` |
| 3 | Page Object 构造函数改写：`PROJECT_NAME` + `urljoin(settings.BASE_URL, url_path)` |
| 4 | 全量替换 `auto_tests.ui_mock` → `auto_tests.pytest_ui_mock` |
| 5 | 更新 `__init__.py`：PROJECT_NAME = `"pytest_ui_mock"` |
| 6 | 更新 `config/settings.py`：类名 `MockUIConfig` → `PytestUIMockConfig` |
| 7 | 新增 `pytest.ini` |

### 阶段 2：bdd_ui_mock 新建

| # | 操作 |
|---|------|
| 1 | 创建目录骨架 |
| 2 | 创建 `__init__.py` + `conftest.py` + `pytest.ini` |
| 3 | 创建 `config/`（复制 + 改类名） |
| 4 | 创建 `page_object/`（复制 + 改导入路径） |
| 5 | 创建 `steps/common/__init__.py` |
| 6 | 创建所有 steps 文件 |
| 7 | 创建所有 Feature 文件 + BDD 绑定文件 |
| 8 | 创建 `data_factory/actions/` |

### 阶段 3：验证

| # | 操作 |
|---|------|
| 1 | 全量搜索 `ui_mock` 引用确保无断裂 |
| 2 | 验证目录结构符合设计 |
