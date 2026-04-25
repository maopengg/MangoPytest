---
alwaysApply: true
---
# API 开发规范
## 必须使用项目已有的虚拟环境的python解释器，不能使用系统默认的python解释器，默认使用项目根目录下的.venv虚拟环境

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

# info - 关键节点
log.info('开始执行测试套件')

# warning - 非关键异常
log.warning(f'资源未找到，使用默认值：{default}')

# error - 错误异常
log.error(f'API请求失败：{error.msg}')
```

---

## 用例编写规范

> ⚠️ **重要：所有 API 用例必须遵循以下五层架构和测试分层规范编写**

### 五层架构

**所有 API 用例必须基于以下五层架构实现：**

```
L5: 用例层 (Test Case)        - 测试执行与断言，调用 L4 Scenario
    ↓ 调用
L4: 场景层 (Scenario)         - 业务编排，使用 L3 Entity 生成/操作数据
    ↓ 使用 L3 生成/操作数据
L3: 实体层 (Entity)           - Pydantic 数据模型 + 业务逻辑，提供 to_api_payload()
    ↓ to_api_payload()
L2: 策略层 (Strategy/Builder) - 接收 L3 Entity，调用 to_api_payload() 后传给 L1
    ↓ 传递 Dict
L1: 接口层 (API Manager)      - HTTP 通信，只接收 Dict，返回 Dict
```

**数据流向说明**：
- L5 调用 L4，L4 使用 L3 创建/操作数据
- L3 通过 `to_api_payload()` 序列化为 Dict
- L2 接收 L3 Entity，调用 `to_api_payload()` 获取 Dict 传给 L1
- L1 只负责 HTTP 通信，不关心 Entity

### 核心设计原则

**1. L3 Entity 是唯一数据定义源头**

- 字段只在 L3 Entity 中定义一次
- 通过 `to_api_payload()` 方法提供给 L1/L2
- L2 Builder 接收 L3 Entity，调用 `to_api_payload()` 获取数据

**2. L3 Entity 使用 Pydantic，提供 `to_api_payload()` 方法**

```python
class OrderEntity(BaseModel):
    order_id: str = ""              # 响应字段，创建后填充
    product_id: int = Field(default=1001, gt=0)  # 请求字段
    
    def to_api_payload(self) -> Dict[str, Any]:
        """请求参数序列化"""
        return {"product_id": self.product_id}
```

> **说明**：order_id 等响应字段在创建时为空，由 L2 Builder 调用 API 后更新到 Entity

**3. L2 Builder 接收 Entity，L1 API 只接收 Dict**

```python
# L2: 接收 Entity，调用 to_api_payload()
class OrderBuilder:
    def create_order(self, entity: OrderEntity) -> OrderEntity:
        payload = entity.to_api_payload()
        result = pytest_api_mock.order.create_order(payload)
        return entity

# L1: 只接收 Dict，不关心 Entity
class OrderAPI:
    def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.post("/api/v1/orders", json=payload)
        return response.json()
```

### 测试分层

| 层级 | 类型 | 占比 | 用途 |
|------|------|------|------|
| L5 | 单接口测试 | 60% | 验证本模块逻辑、边界、异常 |
| L5 | 模块集成测试 | 30% | 验证真实依赖（A→B→C→D） |
| L5 | 端到端测试 | 10% | 验证完整业务闭环 |

### 用例编写原则

**使用 Fixtures**:
```python
# ✅ 使用分层 fixtures 准备数据
def test_create_reimbursement(self, api_client, employee_user, pending_reimbursement):
    pass
```

**Allure 注解**:
```python

@allure.feature("认证模块")
@allure.story("用户登录")
class TestAuthLogin(UnitTest):
    """用户登录接口测试 - 使用新架构"""

    @allure.title("正常登录 - 使用Fixture")
    def test_login_success_with_fixture(self, auth_builder):
        pass

```

**禁止**:
- ❌ 在测试用例中直接调用 API 创建数据（使用 fixtures/builders）
- ❌ 在测试用例中写数据清理逻辑（使用 fixture cleanup）
- ❌ 在测试用例中定义配置常量
- ❌ **不遵守五层架构编写用例（必须通过 L1→L2→L3→L4→L5 分层实现）**
- ❌ **不遵守测试分层比例（单接口60%/集成30%/端到端10%）**
