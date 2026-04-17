# 芒果测试平台 - AI 开发注意事项

## 快速参考

### 常用导入清单

```python
# 日志（最常用）
from core.utils import log
log.info("信息日志")
log.error("错误日志")
log.debug("调试日志")

# 基类
from core.base import BaseEntity, BaseBuilder, BaseStrategy

# 装饰器
from core.decorators import retry, timer, api_case_data

# API 工具
from core.api import APIClient, CaseTool, RequestTool

# 数据模型
from core.models. import ApiDataModel, RequestModel, ResponseModel

# 枚举
from core.enums import MethodEnum, ClientEnum

# 异常
from core.exceptions import ApiError, UiError
from core.exceptions.error_msg import ERROR_MSG_0400
```

---

## 目录结构规范

### 1. 核心模块目录 (core/)

#### 1.1 core/base/ - 基类模块
**用途**: 存放所有全局通用的基类

**现有文件**:
- `base_entity.py` - 实体基类 (BaseEntity)
- `base_builder.py` - Builder 基类 (BaseBuilder)
- `builder_context.py` - Builder 上下文 (BuilderContext)
- `base_strategy.py` - Strategy 基类 (BaseStrategy)
- `strategy_result.py` - 策略执行结果 (StrategyResult)
- `layering_base.py` - 测试分层基类 (UnitTest, IntegrationTest, E2ETest)
- `state_machine.py` - 状态机基类 (State, Transition, StateMachine)
- `web_base.py` - Web UI 基础对象 (WebBaseObject)

**导出规则**:
```python
# 统一从 core.base 导入
from core.base import BaseEntity, BaseBuilder, BaseStrategy
```

**禁止**:
- ❌ 在业务代码中创建新的基类
- ❌ 在 core/base/ 中创建业务相关的类
- ❌ 修改现有基类的核心接口

---

#### 1.2 core/decorators/ - 装饰器模块
**用途**: 存放所有全局通用的装饰器

**现有文件**:
- `api.py` - API 测试装饰器 (case_data, request_data, timer, log_decorator, api_allure_logger)
- `ui.py` - UI 测试装饰器 (case_data)
- `other.py` - 其他测试装饰器 (case_data)
- `utils.py` - 工具装饰器 (retry, singleton, timeit, memoize, throttle, validate_input, log_execution, async_task, cache_result)

**导出规则**:
```python
# 统一从 core.decorators 导入
from core.decorators import retry, singleton, timeit
from core.decorators import api_case_data, ui_case_data
```

**禁止**:
- ❌ 在业务代码中创建新的装饰器
- ❌ 在 tools/decorator/ 目录下创建文件（已删除）

---

#### 1.3 core/api/ - API 客户端模块
**用途**: 存放 API 相关的客户端和工具

**现有文件**:
- `client.py` - API 客户端 (APIClient)
- `auth.py` - 认证管理 (AuthManager)
- `case_tool.py` - API 测试用例工具 (CaseTool)
- `request_tool.py` - HTTP 请求工具 (RequestTool)

**导出规则**:
```python
# 统一从 core.api 导入
from core.api import APIClient, AuthManager, CaseTool, RequestTool
```

**异常处理**:
```python
# 使用全局异常类
from core.exceptions import ApiError, ERROR_MSG_0400
raise ApiError(*ERROR_MSG_0400, "请求超时")
```

---

#### 1.4 core/models/ - 数据模型目录
**用途**: 存放所有 Pydantic 数据模型和 dataclass

**现有文件**:
- `api_model.py` - API 相关模型 (ApiDataModel, RequestModel, ResponseModel, APIResponse)
- `ui_model.py` - UI 相关模型
- `tools_model.py` - 工具相关模型
- `other_model.py` - 其他模型
- `demo_model.py` - pytest_api_mock 专用模型（待拆分）

**导出规则**:
```python
# 统一从 core.models 导入
from core.models. import ApiDataModel, RequestModel, ResponseModel
```

**禁止**:
- ❌ 在业务代码中创建新的数据模型类
- ❌ 在 core/models/ 中混合不同功能的模型

---

#### 1.5 core/enums/ - 枚举目录
**用途**: 存放所有枚举定义

**现有文件**:
- `api_enum.py` - API 相关枚举 (MethodEnum, ClientEnum, IsSchemaEnum)
- `ui_enum.py` - UI 相关枚举
- `tools_enum.py` - 工具相关枚举
- `demo_enum.py` - pytest_api_mock 专用枚举（待拆分）

**导出规则**:
```python
# 统一从 core.enums 导入
from core.enums import MethodEnum, ClientEnum
```

**禁止**:
- ❌ 在业务代码中创建新的枚举类
- ❌ 在 core/enums/ 中混合不同功能的枚举

---

#### 1.6 core/exceptions/ - 异常目录
**用途**: 存放所有异常类和错误消息

**现有文件**:
- `__init__.py` - 异常基类 (PytestAutoTestError, UiError, ApiError, ToolsError, ValidationError, ConfigError, DataError)
- `error_msg.py` - 错误消息定义

**导出规则**:
```python
# 导入异常类
from core.exceptions import ApiError, UiError

# 导入错误消息
from core.exceptions.error_msg import ERROR_MSG_0001, ERROR_MSG_0400

# 抛出异常
raise ApiError(*ERROR_MSG_0400, "请求超时")
```

**禁止**:
- ❌ 创建新的异常类（使用现有的 7 个异常类）
- ❌ 在 core/api/exceptions.py 等位置创建专用异常
- ❌ 在 core/exceptions/__init__.py 中导出错误消息

---

#### 1.7 core/utils/ - 工具模块
**用途**: 存放通用工具函数和日志

**现有文件**:
- `log.py` - 日志对象 (log)
- `helpers.py` - 辅助函数
- `notice.py` - 通知工具
- `main_run.py` - 主运行器
- `obtain_test_data.py` - 测试数据获取
- `project_public_methods.py` - 项目公共方法
- `zip_files.py` - 文件压缩
- `project_dir.py` - 项目目录管理

**导出规则**:
```python
# 统一从 core.utils 导入
from core.utils import log
from core.utils import NoticeMain
```

---

## 开发规范

### 1. 新增功能时的检查清单

- [ ] 是否需要新的基类？→ 如果是，添加到 `core/base/`
- [ ] 是否需要新的装饰器？→ 如果是，添加到 `core/decorators/`
- [ ] 是否需要新的数据模型？→ 如果是，添加到 `core/models/`
- [ ] 是否需要新的枚举？→ 如果是，添加到 `core/enums/`
- [ ] 是否需要新的异常？→ 使用现有的异常类，在 `core/exceptions/error_msg.py` 中添加错误消息
- [ ] 是否需要新的工具函数？→ 如果是，添加到 `core/utils/`

### 2. 文件命名规范

| 目录 | 命名规则 | 示例 |
|------|----------|------|
| core/base/ | `功能_base.py` | `web_base.py`, `state_machine.py` |
| core/decorators/ | `功能.py` | `api.py`, `utils.py` |
| core/api/ | `功能_tool.py` | `case_tool.py`, `request_tool.py` |
| core/models/ | `功能_model.py` | `api_model.py`, `ui_model.py` |
| core/enums/ | `功能_enum.py` | `api_enum.py`, `ui_enum.py` |
| core/exceptions/ | `error_msg.py` | `error_msg.py` |
| core/utils/ | `功能.py` | `log.py`, `helpers.py` |

### 3. 导入规范

**正确示例**:
```python
# 从统一入口导入
from core.base import BaseEntity, BaseBuilder
from core.decorators import retry, api_case_data
from core.api import APIClient, CaseTool
from core.models. import ApiDataModel
from core.enums import MethodEnum
from core.exceptions import ApiError
from core.exceptions.error_msg import ERROR_MSG_0400
from core.utils import log
```

**错误示例**:
```python
# ❌ 从具体文件导入（除非必要）
from core.base.base_entity import BaseEntity
from core.decorators.api import case_data
from core.models.api_model import ApiDataModel
```

### 4. 业务代码规范

**业务代码应该**:
- ✅ 使用现有的基类、装饰器、模型、枚举、异常
- ✅ 在 `auto_tests/pytest_api_mock/` 中实现业务逻辑
- ✅ 通过继承和组合使用现有组件

**业务代码不应该**:
- ❌ 创建新的基类、装饰器、模型、枚举、异常
- ❌ 修改核心模块的代码
- ❌ 在核心模块中添加业务逻辑

---

## 错误消息规范

### 错误消息编号规则

| 编号范围 | 用途 |
|----------|------|
| 0001-0099 | 通用错误 |
| 0100-0199 | UI 测试错误 |
| 0200-0299 | 数据库错误 |
| 0300-0399 | 元素/页面错误 |
| 0400-0499 | API 请求错误（HTTP 状态码对应） |
| 0500-0599 | 服务器错误（HTTP 状态码对应） |

### 添加错误消息示例

```python
# 在 core/exceptions/error_msg.py 中添加
ERROR_MSG_0400 = (400, 'API 请求失败：{}')
ERROR_MSG_0401 = (401, 'API 认证失败：{}')
```

---

## 总结

1. **核心模块** (`core/`) 只存放**全局通用**的组件
2. **业务代码** (`auto_tests/pytest_api_mock/`) 只使用现有组件，不创建新组件
3. **统一导入** 从模块的 `__init__.py` 导入，不从具体文件导入
4. **异常处理** 使用现有的 7 个异常类 + `core/exceptions/error_msg.py` 中的错误消息
5. **新增功能** 先检查是否可以使用现有组件，确实需要再创建

---

## 附录：现有组件清单

### 基类 (core/base/)
- BaseEntity, BaseBuilder, BuilderContext
- BaseStrategy, StrategyResult
- TestLayer, UnitTest, IntegrationTest, E2ETest, TestContext, TestCaseResult, TestLayerType
- State, Transition, TransitionResult, StateMachine
- WebBaseObject

### 装饰器 (core/decorators/)
- api_case_data, request_data, timer, log_decorator, api_allure_logger
- ui_case_data, other_case_data
- retry, singleton, deprecated, timeit, memoize, throttle, validate_input, log_execution, async_task, cache_result

### 异常 (core/exceptions/)
- PytestAutoTestError, UiError, ApiError, ToolsError, ValidationError, ConfigError, DataError
- ERROR_MSG_0001 ~ ERROR_MSG_0504

### 枚举 (core/enums/)
- MethodEnum, ClientEnum, IsSchemaEnum
- 其他 UI、Tools、Demo 相关枚举

### 模型 (core/models/)
- ApiDataModel, RequestModel, ResponseModel, APIResponse
- 其他 UI、Tools、Other、Demo 相关模型

### 日志 (core/utils/log.py)
**导入方式**:
```python
from core.utils import log
```

**使用方法**:
```python
log.debug("调试信息")
log.info("普通信息")
log.warning("警告信息")
log.error("错误信息")
log.critical("严重错误")
```

**注意**:
- ✅ 所有模块都应该使用统一的日志对象
- ✅ 使用适当的日志级别
- ❌ 不要创建新的日志实例
