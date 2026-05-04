---
alwaysApply: true
---
# BDD API Mock 用例编写规范

## 环境要求
- 使用项目根目录下的 `.venv` 虚拟环境

## 日志使用规范

### 使用原则
- ✅ **优先使用 `debug`** - 大部分日志应该是 debug 级别，避免 info 过多
- ✅ 循环内部、频繁调用的方法必须使用 `debug`
- ✅ 关键业务节点（开始/结束/结果）使用 `info`
- ✅ 异常处理中使用 `error` 或 `warning`

### 示例
```python
from core.utils import log

# debug - 内部流程
log.debug(f'开始查询用例：{case_id}')
```

## 五层架构（必须遵守）

```
L5: Feature 文件（Gherkin 中文语法）
    ↓
L4: Steps 步骤定义层（common/api/auth/data/assertions）
    ↓
L3: Data Factory（entities/factories/specs）
    ↓
L2: Repositories（按业务域分包，自动清理）
    ↓
L1: 数据库（MySQL）
```

## 目录结构

```
├── features/          # Feature 文件（Gherkin 语法）
├── steps/             # 步骤定义层
│   ├── common/        # 通用 fixtures
│   ├── api/           # API 请求步骤
│   ├── auth/          # 认证步骤
│   ├── data/          # 数据准备步骤
│   └── assertions/    # 断言步骤
├── data_factory/      # 数据工厂层
│   ├── entities/      # SQLAlchemy ORM 实体
│   ├── factories/     # Factory 基类
│   └── specs/         # pytest-factoryboy Spec
├── repos/             # Repository 数据访问层
└── hooks/             # 测试钩子（数据清理）
```

## 编写原则

### 1. Feature 文件规范
- 使用中文 Gherkin 语法（`# language: zh-CN`）
- 使用占位符传递数据：`${{entity.id}}`
- 示例：
```gherkin
# language: zh-CN
功能: 用户管理
  场景: 获取用户详情
    假如 存在"用户"
    当 使用用户ID GET "/users/${{user.id}}"
    那么 响应状态码应该为 200
```

### 2. 数据创建规范
- 使用 Factory 创建测试数据：`假如 存在"用户"`
- 测试数据以 `AUTO_` 开头，便于自动清理
- 禁止在测试用例中直接调用 API 创建数据

### 3. 测试分层比例（必须遵守）
| 类型 | 占比 |
|------|------|
| 单接口测试 | 60% |
| 模块集成测试 | 30% |
| 端到端测试 | 10% |

## 禁止
- ❌ 在测试用例中直接调用 API 创建数据
- ❌ 在测试用例中写数据清理逻辑
- ❌ 在测试用例中定义配置常量
- ❌ 不遵守五层架构
- ❌ 不遵守测试分层比例
