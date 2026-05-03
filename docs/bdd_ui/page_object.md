# Page Object — 页面对象设计

## 职责

封装页面元素定位和操作，提供业务方法供步骤调用。对应 BDD API 模式中的 data_factory 层。

## 设计思路

```
步骤: user_enter_click_page()
  → ClickPage(base_data, test_data)
  → self.element("双击按钮")   # 从飞书/配置文件获取定位器
  → self.w_click(locator)      # 调用 Playwright 执行操作
```

## 目录结构

```
page_object/
├── home.py          # 首页
├── click.py         # 点击操作页面
├── alert.py         # 弹窗页面
├── input.py         # 输入框页面
└── ...
```

## 写法

### 标准模板

```python
from urllib.parse import urljoin
from mangoautomation.uidrive import BaseData

from auto_tests.<project> import PROJECT_DISPLAY_NAME
from auto_tests.<project>.config import settings
from core.ui import WebBaseObject
from core.utils.obtain_test_data import ObtainTestData


class HomePage(WebBaseObject):

    def __init__(self, base_data: BaseData, test_data: ObtainTestData):
        project_name = PROJECT_DISPLAY_NAME   # 飞书文档项目名
        module_name = "模拟首页"              # 飞书文档模块名
        page_name = "首页"                    # 飞书文档页面名
        url_path = "/"                        # URL 路径
        self.base_data = base_data
        self.test_data = test_data
        super().__init__(project_name, module_name, page_name, self.base_data, test_data)
        self.url = urljoin(settings.BASE_URL, url_path)

    def goto(self):
        """打开页面"""
        self.base_data.page.goto(self.url, timeout=30000)
```

### 构造函数规范

| 参数 | 来源 | 用途 |
|------|------|------|
| `project_name` | `PROJECT_DISPLAY_NAME` | 飞书文档中定位元素的项目名 |
| `module_name` | 硬编码字符串 | 飞书文档中定位元素的模块名 |
| `page_name` | 硬编码字符串 | 飞书文档中定位元素的页面名 |
| `url_path` | 硬编码字符串 | 页面 URL 路径片段 |
| `self.url` | `urljoin(settings.BASE_URL, url_path)` | 完整 URL |

### 业务方法

```python
class ClickPage(WebBaseObject):

    def test_double_click(self):
        """双击操作"""
        self.w_dblclick(self.element("双击按钮"))
        return self.w_get_text(self.element("结果"))

    def test_right_click(self):
        """右键操作"""
        self.w_right_click(self.element("右键点击按钮"))
        return self.w_get_text(self.element("结果"))
```

**原则**：方法做完整操作并返回结果，供步骤层断言。

### 元素定位

```python
self.element("元素名称")
# → 从飞书文档查询定位器
# → 项目名/模块名/页面名/元素名 四级定位
# → 返回 Playwright Locator
```

### 断言封装

```python
class ContractTypePage(WebBaseObject):

    def verify_create_success(self):
        """验证创建成功提示出现"""
        self.web_ass.a_assert_ele_exists(
            self.element("创建成功提示")
        )
```

复杂断言封装在 Page Object 方法中，步骤层只调用不写断言逻辑。

## 注意事项

- Page Object 不持有步骤状态（用 `page_context` / `test_data_context` 传递）
- 每个 Page Object 对应一个页面，不是对应一个操作
- `goto()` 方法只导航不操作，业务操作在独立方法中
