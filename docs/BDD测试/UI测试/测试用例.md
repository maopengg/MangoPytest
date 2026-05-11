# Test Cases — Feature 文件与 BDD 绑定

## 职责

测试用例层，每个模块一个子目录。

## 目录结构

```
test_cases/
├── home/
│   ├── home.feature
│   └── test_home_bdd.py
├── click/
│   ├── click.feature
│   └── test_click_bdd.py
└── ...
```

## 测试分层

用例设计遵循三层金字塔，详见 [测试分层](../test_layering.md)。

```
API (60%) → Integration (30%) → E2E (10%)
```

UI 测试同理：
- 单页面正向/负向 → `@smoke @positive` / `@negative`
- 多页面串联流程 → `@integration`
- 完整业务操作闭环 → `@e2e`

## Feature 文件格式

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
  场景: 悬停元素
    当 用户进入元素点击页面
    而且 用户执行悬停操作
    那么 悬停操作应该成功
```

## BDD 绑定文件

```python
import allure
from pytest_bdd import scenarios

pytestmark = [
    allure.epic("BDD UI Mock 测试"),
    allure.feature("元素点击"),
    allure.story("点击操作验证"),
]

scenarios("click.feature")
```

## Marker 标签

| 标签 | 含义 | CI 策略 |
|------|------|---------|
| `@smoke` | 冒烟测试 | 每次提交必跑 |
| `@ui` | UI 自动化标记 | — |
| `@positive` | 正向场景 | 每次提交必跑 |
| `@negative` | 负向场景 | 每次提交必跑 |
| `@integration` | 集成测试 | 合分支时跑 |
| `@e2e` | 端到端 | 定时/发布前跑 |
