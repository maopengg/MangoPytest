# bdd_api 大型项目改造方案

## 实施进度（2026-08-23）

- [x] 删除 4 条过期 `xfail`，远程全量回归达到 165 passed。
- [x] `products` 的 8 条场景迁移为真实中文 Feature 与领域 Steps。
- [x] 建立商品 Entity、Spec、Factory、Repository 标准模板。
- [x] 删除集中执行器中 FTAPI-0015～0022 的旧编号分支。
- [x] `cross_protocol` 使用有名称的检查结果，11 条远程通过。
- [ ] 依次迁移 auth/test_runs、orders、claims/reviews 和协议实验域。
- [ ] 完成配置安全、Allure 请求附件和质量门禁改造。

## 1. 项目定位

`bdd_api` 定位为面向业务协作的大型 API 自动化方案：产品、测试、开发可以通过中文 Gherkin 共同评审场景，Python 代码负责数据准备、协议调用、业务编排和断言实现。

本次改造保留以下特征：

- 保留 `pytest-bdd` 和中文 Feature。
- 保留现有 165 个用例 ID，迁移期间不减少覆盖率。
- 保留 HTTP、WebSocket、SSE、MCP、gRPC 和跨协议场景。
- 保留本项目独立的数据工厂和业务 Repository。
- 底层协议继续复用 `auto_tests/common/mango_mock/`，不复制客户端。

本方案不要求与 `pytest_api` 合并。两个项目展示不同自动化方式，业务 Case 和数据工厂允许重复。

## 2. 当前主要问题

### P0：当前完整回归会失败

远程 Mango Mock 已修复，但 FTAPI-0092、0130、0131、0138 仍保留 `xfail(strict=True)`，正常执行会产生 `XPASS(strict)`。

### P1：多数 Feature 只是 BDD 外壳

当前大量场景只有统一步骤：

```gherkin
当 执行功能用例 "FTAPI-0015"
那么 标准化响应状态码为 200
并且 标准化业务 code 为 0
并且 所有功能期望均成立
```

真实请求和断言隐藏在按编号分支的 Handler 中，Feature 无法独立表达业务行为。

### P1：目录主要按协议组织，没有完全按业务域组织

`FunctionalCaseRepository` 同时负责商品、订单、审批、审查、Webhook 和多协议操作。大型团队下会形成多人修改热点。

### P1：断言信息不足

`FunctionalCaseResult` 把真实结果转换成无名称的 `list[bool]`，失败时不容易定位预期字段、实际字段和接口响应。

### P2：配置和运行治理不足

- Token、账号和数据库密码存在默认明文值。
- test/pre 默认继承 prod 配置。
- gRPC 地址通过 HTTP 主机加固定 `50051` 得出。
- 缺少统一的 Ruff、类型检查、覆盖率和 Feature 一致性门禁。

## 3. 目标架构

项目采用“业务域优先、协议能力下沉”的结构：

```text
auto_tests/api/bdd_api/
├── config/
│   ├── settings.py
│   └── environments/
├── features/                         # L5：中文业务场景
│   ├── auth/
│   ├── catalog/
│   ├── order/
│   ├── approval/
│   ├── review/
│   └── protocol_lab/
├── steps/                            # L4：步骤定义
│   ├── common/
│   ├── auth/
│   ├── catalog/
│   ├── order/
│   ├── approval/
│   ├── review/
│   └── assertions/
├── data_factory/                     # L3：实体、规格、工厂
│   ├── entities/
│   │   ├── product.py
│   │   ├── order.py
│   │   └── claim.py
│   ├── specs/
│   └── factories/
├── repositories/                     # L2：按业务域封装访问
│   ├── auth_repository.py
│   ├── product_repository.py
│   ├── order_repository.py
│   ├── claim_repository.py
│   ├── review_repository.py
│   └── webhook_repository.py
├── workflows/                        # 跨业务/跨协议编排
│   ├── approval_workflow.py
│   └── review_workflow.py
├── fixtures/
│   ├── runtime.py
│   ├── auth.py
│   └── domain.py
├── test_cases/                       # Feature 绑定和 pytest marks
└── conftest.py                       # 只注册插件，不承载业务逻辑
```

依赖方向固定为：

```text
Feature → Steps → Factory/Workflow → Repository → common/mango_mock
```

禁止反向依赖，Steps 不得访问 `runtime.http`、`runtime.grpc` 等客户端私有实现。

## 4. 标准场景写法

### Feature

```gherkin
# language: zh-CN
功能: 商品管理

  背景:
    假如 已创建隔离测试运行
    并且 员工已登录

  @smoke @positive @http
  场景: FTAPI-0015 使用唯一 SKU 创建商品
    假如 已生成唯一商品数据
    当 用户创建商品
    那么 响应状态码应该为 201
    并且 响应字段 "code" 应该为 "0"
    并且 响应数据 "sku" 应该等于生成的商品 SKU
```

### Step

```python
@when("用户创建商品", target_fixture="api_response")
def create_product(product_factory, product_repository):
    product = product_factory.build()
    response = product_repository.create(product)
    return {
        "response": response,
        "status_code": response.status_code,
        "data": response.json().get("data"),
        "expected": product,
    }
```

### Repository

```python
class ProductRepository:
    def __init__(self, runtime):
        self._runtime = runtime

    def create(self, product: ProductEntity):
        return self._runtime.http.request_raw(
            "POST",
            "/api/v1/products",
            run_id=self._runtime.run_id,
            token=self._runtime.token("employee"),
            json=product.to_request(),
        )
```

## 5. 数据工厂标准

每个核心业务域至少包含：

- Entity：强类型业务对象。
- Spec：合法、边界、非法数据规格。
- Factory：生成唯一数据，默认以 `AUTO_` 开头。
- Repository：创建、查询和清理数据。

示例：

```python
class ProductEntity(BaseModel):
    sku: str
    name: str
    price: Decimal
    stock: int

    def to_request(self) -> dict:
        return self.model_dump(mode="json")
```

禁止：

- 在 Feature 绑定文件中准备数据。
- 在 Step 中直接创建 `httpx.Client`。
- 在 Factory 中写断言。
- 在测试文件中写清理逻辑。

## 6. 响应和断言标准

取消固定 `status_code=200`、`code=0` 的包装结果，保存真实响应。

优先使用已有 DAL：

```gherkin
那么 响应应该为:
  """
  status_code = 201
  body.code = 0
  body.data.id > 0
  body.data.sku = context.product.sku
  """
```

如果需要组合检查，必须使用有名称的结果：

```python
checks = {
    "status_code": response.status_code == 201,
    "business_code": body["code"] == 0,
    "sku": body["data"]["sku"] == product.sku,
}
```

Allure 失败附件至少包含请求方法、URL、脱敏请求头、请求体、响应状态码和响应体。

## 7. 配置与安全改造

配置文件只声明字段，不提供真实 Secret：

```python
class MockSettings(BaseSettings):
    http_base_url: AnyHttpUrl
    websocket_url: str | None = None
    mcp_url: AnyHttpUrl | None = None
    grpc_target: str
    grpc_tls: bool = False
    admin_token: SecretStr
```

要求：

- dev/test/pre/prod 地址完全分开。
- CI Secret 注入管理员 Token、账号和数据库密码。
- 禁止 test/pre 缺省回退到 prod。
- 日志自动脱敏 `Authorization`、Token、Cookie、密码。
- 已提交过的真实密码应轮换。

## 8. 迁移步骤

### 阶段 0：恢复绿色基线

1. 删除 4 条已修复用例的旧 xfail。
2. 保证 165 条全部通过。
3. 增加用例 ID 唯一性和 Feature 绑定检查。

### 阶段 1：建立标准模板

1. 选择 `products` 作为 HTTP 标准业务域。
2. 选择 `cross_protocol` 作为跨协议标准业务域。
3. 建立 Entity、Spec、Factory、Repository、Steps 模板。
4. 增加请求/响应 Allure 附件。

### 阶段 2：迁移核心业务

按以下顺序逐域迁移：

1. auth、test_runs。
2. products、orders。
3. claims、reviews。
4. webhooks、faults。
5. SSE、WebSocket、MCP、gRPC Lab。

每迁移一个域就删除该域在 `FunctionalCaseExecutor` 中的编号分支，不保留双实现。

### 阶段 3：删除通用编号执行器

- 删除“执行功能用例 ID”通用 Step。
- 删除 `FunctionalCaseResult.checks: list[bool]`。
- 删除按编号上限路由的 Handler。
- 所有 Feature 改为真实 Given/When/Then。

### 阶段 4：大型项目门禁

- Ruff 格式和静态检查。
- 类型检查。
- pytest collection 检查。
- `pytest -n auto` 并行回归。
- 覆盖率阈值。
- xfail 必须填写负责人、原因和到期日期。
- 生成 Allure 报告并保留历史趋势。

## 9. 验收标准

- 165 个原用例 ID 全部保留且无非预期 xfail。
- Feature 中不再出现“执行功能用例 FTAPI-xxxx”通用步骤。
- Steps 中没有 `httpx.Client`、WebSocket `connect()` 或 gRPC Stub 创建。
- Repository 按业务域拆分，单文件建议不超过 300 行。
- 每个核心业务域都有 Entity、Spec、Factory 和 Repository。
- Feature 断言使用真实 HTTP/业务响应，不断言固定包装值。
- `ENV=test` 不可能连接生产数据库。
- 仓库不包含真实密码和管理员 Token。
- 串行和 `-n auto` 执行结果一致。
- 新人可只参考一个标准业务域完成新模块接入。

## 10. 主要风险

- 一次性重写 165 条容易丢失覆盖，应按业务域渐进迁移。
- BDD 步骤过度复用会再次变成隐藏业务逻辑的“万能 Step”。
- Steps 过细会导致步骤数量膨胀，应复用技术步骤，保留业务语义。
- 并行执行必须继续依赖 Test Run 隔离，禁止共享可变全局数据。

## 11. 改造完成后的适用范围

完成本方案后，`bdd_api` 适合：

- 业务人员参与用例评审。
- 多团队按业务域维护。
- 500～3000 条 API/多协议场景。
- 需要需求可追溯、Allure 报告和跨协议验收的项目。
