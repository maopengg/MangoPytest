# Allure 集成指南

## 概述

本项目已集成 Allure 报告框架，将以下架构功能可视化到测试报告中：

1. **Context 操作** - create/use/action/expect/event 自动记录
2. **数据血缘追踪** - 数据依赖关系图自动附加
3. **场景变体信息** - 变体矩阵参数自动记录
4. **状态机流转** - 状态转换历史自动附加
5. **构造器依赖** - 依赖链自动记录

## 安装

```bash
pip install allure-pytest
```

## 快速开始

### 1. 运行测试并生成 Allure 报告

```bash
# 执行测试并生成 Allure 结果
python -m pytest auto_test/demo_project/test_cases/ -v --alluredir=./allure-results

# 查看 Allure 报告
allure serve ./allure-results
```

### 2. 使用 Allure 集成 Fixtures

在测试中使用 `allure_context` fixture 自动记录 Context 操作：

```python
from auto_test.demo_project.fixtures.allure_conftest import allure_feature, allure_story

@allure_feature("用户管理")
@allure_story("用户创建")
def test_create_user(allure_context):
    """创建用户并验证"""
    # 创建用户（自动记录到 Allure）
    user = allure_context.create(UserEntity, username="test", role="admin")
    
    # 验证（自动记录到 Allure）
    assert user.role == "admin"
```

### 3. 手动记录步骤

使用 `AllureHelper` 手动记录步骤和附件：

```python
from auto_test.demo_project.core.allure_integration import AllureHelper, allure_step

def test_manual_steps():
    # 记录步骤
    with allure_step("准备数据"):
        data = {"username": "test"}
        AllureHelper.attach_json("测试数据", data)
    
    # 记录文本
    with allure_step("执行操作"):
        AllureHelper.attach_text("操作结果", "成功")
    
    # 记录 HTML
    with allure_step("生成报告"):
        AllureHelper.attach_html("报告", "<h1>测试报告</h1>")
```

## 核心模块

### AllureHelper

统一的 Allure 辅助类：

```python
from auto_test.demo_project.core.allure_integration import AllureHelper

# 标记功能和故事
AllureHelper.feature("用户管理")
AllureHelper.story("用户创建")

# 设置标题和描述
AllureHelper.title("创建用户测试")
AllureHelper.description("测试创建新用户的功能")

# 记录步骤
with AllureHelper.step("创建用户"):
    pass

# 附加数据
AllureHelper.attach_json("数据", {"key": "value"})
AllureHelper.attach_text("文本", "内容")
AllureHelper.attach_html("HTML", "<h1>标题</h1>")
```

### ContextAllureAdapter

自动记录 Context 操作：

```python
from auto_test.demo_project.core.allure_integration import ContextAllureAdapter

adapter = ContextAllureAdapter(context)

# 记录创建操作
adapter.record_create("UserEntity", "user_001", username="test")

# 记录复用操作
adapter.record_use("UserEntity", "user_001", role="admin")

# 记录业务动作
adapter.record_action("login", "user_001", True)

# 记录预期验证
adapter.record_expect("user.role == 'admin'", True)

# 记录事件触发
adapter.record_event("user_created", "normal", True)

# 附加操作摘要
adapter.attach_summary()
```

### LineageAllureAdapter

自动记录数据血缘：

```python
from auto_test.demo_project.core.allure_integration import LineageAllureAdapter

# 附加血缘图
LineageAllureAdapter.attach_lineage_graph(tracker)

# 附加血缘分析
LineageAllureAdapter.attach_lineage_analysis(tracker)
```

### VariantAllureAdapter

自动记录变体信息：

```python
from auto_test.demo_project.core.allure_integration import VariantAllureAdapter

# 附加变体信息
VariantAllureAdapter.attach_variant_info("admin_correct", {"role": "admin", "password": "correct"})

# 附加变体矩阵
VariantAllureAdapter.attach_variant_matrix(matrix)
```

### StateMachineAllureAdapter

自动记录状态转换：

```python
from auto_test.demo_project.core.allure_integration import StateMachineAllureAdapter

# 附加状态转换历史
StateMachineAllureAdapter.attach_state_transitions(state_machine)
```

### BuilderAllureAdapter

自动记录构造器依赖：

```python
from auto_test.demo_project.core.allure_integration import BuilderAllureAdapter

# 附加构造器依赖链
BuilderAllureAdapter.attach_builder_dependencies(builder)
```

## Fixtures

### allure_context

自动记录 Context 操作的 fixture：

```python
def test_with_allure_context(allure_context):
    """Context 操作自动记录到 Allure"""
    user = allure_context.create(UserEntity, username="test")
    assert user.username == "test"
```

### allure_lineage

自动记录血缘信息的 fixture：

```python
def test_with_allure_lineage(allure_context, allure_lineage):
    """血缘信息自动附加到 Allure"""
    user = allure_context.create(UserEntity, username="test")
    # 测试结束后血缘信息自动附加
```

### allure_variant

自动记录变体信息的 fixture：

```python
@pytest.mark.parametrize("variant", LoginScenario.all_variants())
def test_with_allure_variant(allure_variant, variant):
    """变体信息自动附加到 Allure"""
    pass
```

## 装饰器

### @allure_feature

标记功能模块：

```python
from auto_test.demo_project.fixtures.allure_conftest import allure_feature

@allure_feature("用户管理")
class TestUser:
    pass
```

### @allure_story

标记用户故事：

```python
from auto_test.demo_project.fixtures.allure_conftest import allure_story

@allure_story("用户创建")
def test_create_user():
    pass
```

## 示例

完整示例见 `test_cases/test_allure_integration.py`：

```bash
python -m pytest auto_test/demo_project/test_cases/test_allure_integration.py -v --alluredir=./allure-results
allure serve ./allure-results
```

## 报告内容

Allure 报告将包含：

1. **测试概览** - 测试总数、通过率、失败率
2. **功能分类** - 按 feature/story 分类的测试
3. **Context 操作** - 每个测试的 create/use/action/expect/event 操作
4. **血缘信息** - 数据依赖关系图和分析
5. **变体信息** - 变体矩阵参数
6. **状态转换** - 状态机流转历史
7. **构造器依赖** - 依赖链信息
8. **附件** - JSON/文本/HTML 格式的详细数据

## 最佳实践

1. **使用 @allure_feature/@allure_story** - 为测试分类
2. **使用 allure_context fixture** - 自动记录 Context 操作
3. **使用 allure_lineage fixture** - 自动记录血缘信息
4. **编写清晰的 docstring** - 作为测试描述
5. **使用 AllureHelper.step** - 记录关键步骤
6. **附加关键数据** - 使用 attach_json/attach_text/attach_html

## 故障排除

### 报告为空

确保安装了 allure-pytest：

```bash
pip install allure-pytest
```

### 步骤没有显示

确保使用了 `AllureHelper.step()` 或 `allure_step()`：

```python
from auto_test.demo_project.core.allure_integration import allure_step

with allure_step("步骤名称"):
    # 步骤内容
    pass
```

### 附件没有显示

确保使用了正确的 attachment_type：

```python
AllureHelper.attach_json("名称", data)  # JSON
AllureHelper.attach_text("名称", text)  # 文本
AllureHelper.attach_html("名称", html)  # HTML
```

## 参考

- [Allure 官方文档](https://docs.qameta.io/allure/)
- [pytest-allure 插件](https://github.com/allure-framework/allure-pytest)
