# pytest_api 大型项目改造方案

## 实施进度（2026-08-23）

- [x] 全局规范已允许纯 pytest 五层架构。
- [x] 建立 `services/` 业务编排层。
- [x] `products` 的 8 条用例迁移为纯 pytest，并建立领域 Entity、Spec、Factory、Repository、Service。
- [x] `cross_protocol` 的 11 条用例迁移为纯 pytest Workflow。
- [x] 其余 146 条用例全部迁移为纯 pytest 领域/协议 Service。
- [x] 删除全部 `features/`、`steps/`、BDD 插件注册和集中执行器。
- [x] Service 只通过 Repository 公开方法调用公共协议客户端。
- [x] Pydantic 配置升级为 V2 `ConfigDict`，消除 5 条弃用警告。
- [x] 保持完整 165 条收集，远程全量回归结果为 165 passed、0 warnings。
- [x] `pytest -n 4` 并行隔离回归结果为 165 passed、0 warnings。

## 1. 项目定位

`pytest_api` 定位为面向技术团队的大型纯 pytest 自动化方案，强调强类型、参数化、Fixture 组合、业务服务编排和数据依赖管理。

它必须与 `bdd_api` 形成明确差异：

| 项目 | 用例入口 | 主要用户 | 核心优势 |
|---|---|---|---|
| `bdd_api` | 中文 Feature | 业务、测试、开发 | 业务可读、需求可追溯 |
| `pytest_api` | Python 测试函数 | 测试开发、研发 | 强类型、参数化、重构友好 |

本项目保留独立 Case 和数据工厂；仅底层协议复用 `auto_tests/common/mango_mock/`。

## 2. 实施前提

当前项目级 `AGENTS.md` 强制所有项目使用 Feature → Steps 五层架构。实施纯 pytest 方案前，应先把规范调整为“按项目模式选择架构”：

- `bdd_api`：Feature → Steps → Factory → Repository → Data/Protocol。
- `pytest_api`：Tests → Services → Factory → Repository → Data/Protocol。

否则纯 pytest 方案会与全局规范冲突。

## 3. 当前主要问题

### P0：项目仍是 pytest-bdd

Feature 和测试绑定与 `bdd_api` 基本一致，测试文件仍导入 `pytest_bdd.scenario`。目前并没有给用户提供真正独立的 pytest 模式。

### P0：集中执行器不可扩展

`steps/api/functional_case_executor.py` 超过 600 行，通过 FTAPI 编号区间分发所有业务和协议场景，是大型团队的代码冲突热点。

### P1：五层数据工厂没有真正落地

当前 Factory 主要生成字典，缺少按业务域划分的请求 Entity、响应 Entity、Spec、依赖关系和场景 Service。

### P1：执行器绕过 Repository

部分代码直接访问 `runtime.sse`、`runtime.mcp`、gRPC Stub、客户端私有字段和原生 `connect()`，导致协议实现泄漏到用例编排层。

### P1：配置存在明文 Secret 和生产环境回退

这不满足大型项目的安全和环境隔离要求。

## 4. 目标五层架构

```text
L5  tests/                 纯 pytest 用例、marks、参数化和断言
 ↓
L4  services/              业务场景与跨协议工作流
 ↓
L3  data_factory/          entities/specs/factories/依赖组合
 ↓
L2  repositories/          按业务域封装接口和数据访问
 ↓
L1  common/mango_mock/     HTTP/WS/SSE/MCP/gRPC 公共协议客户端
     database/             可选的测试数据数据库 Gateway
```

依赖只能向下：测试不能直接访问公共协议客户端，Factory 不能依赖测试文件。

## 5. 目标目录

```text
auto_tests/api/pytest_api/
├── config/
│   ├── settings.py
│   └── environments/
├── models/
│   ├── auth.py
│   ├── product.py
│   ├── order.py
│   ├── claim.py
│   └── review.py
├── data_factory/
│   ├── entities/
│   ├── specs/
│   ├── factories/
│   └── scenarios/
├── repositories/
│   ├── auth_repository.py
│   ├── product_repository.py
│   ├── order_repository.py
│   ├── claim_repository.py
│   ├── review_repository.py
│   └── protocol_lab/
│       ├── http_lab_repository.py
│       ├── websocket_repository.py
│       ├── sse_repository.py
│       ├── mcp_repository.py
│       └── grpc_repository.py
├── services/
│   ├── product_service.py
│   ├── order_service.py
│   ├── approval_workflow.py
│   └── review_workflow.py
├── fixtures/
│   ├── runtime.py
│   ├── repositories.py
│   ├── factories.py
│   └── domain.py
├── tests/
│   ├── auth/
│   ├── products/
│   ├── orders/
│   ├── approval/
│   ├── reviews/
│   ├── protocol_lab/
│   └── cross_protocol/
├── conftest.py
└── pytest.ini
```

改造完成后删除本项目的 `features/`、`steps/` 和 Feature 绑定文件。

## 6. 标准模型

请求模型和响应模型分开，禁止用一个 dict 同时表达两者。

```python
class ProductCreate(BaseModel):
    sku: str
    name: str
    price: Decimal = Field(ge=0)
    stock: int = Field(ge=0)


class ProductView(ProductCreate):
    id: int
    version: int
```

Repository 返回统一响应对象：

```python
class RepositoryResult(Generic[T]):
    status_code: int
    code: int | str | None
    data: T | None
    headers: Mapping[str, str]
    raw: Any
```

不允许把真实响应转换成固定的 `status_code=200`、`code=0`。

## 7. Repository 标准

Repository 只负责单一业务域的原子操作：

```python
class ProductRepository:
    def __init__(self, runtime):
        self._runtime = runtime

    def create(self, payload: ProductCreate) -> RepositoryResult[ProductView]:
        response = self._runtime.http.request_raw(
            "POST",
            "/api/v1/products",
            run_id=self._runtime.run_id,
            token=self._runtime.token("employee"),
            json=payload.model_dump(mode="json"),
        )
        return RepositoryResult.from_http(response, ProductView)
```

禁止：

- 测试直接调用 `runtime.http`。
- Service 访问 `_client`、`_channel`、`_headers` 等私有属性。
- Repository 同时负责多个不相关业务域。
- Repository 内编写 pytest 断言。

## 8. Service 和工作流标准

Service 负责组合 Repository，不关心 pytest：

```python
class ApprovalWorkflow:
    def __init__(self, claim_repo, approval_repo):
        self.claim_repo = claim_repo
        self.approval_repo = approval_repo

    def approve_large_claim(self, claim: ClaimCreate) -> ApprovalTrace:
        created = self.claim_repo.create(claim)
        stages = []
        for role in ("dept_manager", "finance_manager", "ceo"):
            stages.append(self.approval_repo.approve(created.data.id, role))
        return ApprovalTrace(created=created.data, stages=stages)
```

跨协议工作流也放在 Service 层，测试只断言业务结果。

## 9. 测试标准

### 单场景测试

```python
@pytest.mark.integration
@pytest.mark.http
@allure.id("FTAPI-0015")
def test_create_product_with_unique_sku(product_factory, product_repository):
    expected = product_factory.build_create()
    result = product_repository.create(expected)

    assert result.status_code == 201
    assert result.code == 0
    assert result.data.sku == expected.sku
```

### 参数化边界测试

```python
@pytest.mark.parametrize(
    ("price", "expected_status", "expected_code"),
    [
        (Decimal("0"), 201, 0),
        (Decimal("-0.01"), 422, "VALIDATION_ERROR"),
    ],
    ids=["zero-price", "negative-price"],
)
def test_product_price_boundary(
    price,
    expected_status,
    expected_code,
    product_factory,
    product_repository,
):
    product = product_factory.build_create(price=price)
    result = product_repository.create(product)
    assert result.status_code == expected_status
    assert result.code == expected_code
```

要求：

- 每条测试保留 FTAPI ID，可通过 `allure.id` 或自定义 marker 关联 Excel Case。
- 一个测试只验证一个清晰业务目标。
- 前置数据由 Fixture/Factory 提供。
- 清理由 Fixture/Repository 统一处理。
- 失败时附加完整但脱敏的请求响应。

## 10. Fixture 设计

Fixture 按生命周期分层：

| Scope | 内容 |
|---|---|
| session | 只读配置、协议客户端工厂、Schema 缓存 |
| module | 无可变状态的业务服务模板 |
| function | Test Run、Token、Repository、测试数据 |

Test Run 必须保持 function scope，以支持并行隔离。

清理必须使用 `try/finally`：

```python
@pytest.fixture
def runtime(settings):
    value = MangoMockRuntime(settings).start()
    try:
        yield value
    finally:
        value.close()
```

`close()` 内部即使远程清理失败，也必须关闭 HTTP、MCP 和 gRPC 连接。

## 11. 数据工厂和复杂依赖

数据工厂负责构造数据，不执行断言：

```text
ProductFactory → ProductCreate
OrderFactory(ProductView) → OrderCreate
ClaimFactory(UserView) → ClaimCreate
ReviewFactory → ReviewStart
```

复杂依赖通过 Scenario Factory 或 Service 组合：

```python
@dataclass
class OrderScenario:
    product: ProductView
    order: OrderView
```

所有生成数据以 `AUTO_` 开头，并记录：

- 创建来源。
- Test Run ID。
- 业务主键。
- 清理状态。

## 12. 配置与安全

配置要求与 BDD 项目一致：

- HTTP、WebSocket、MCP、gRPC 独立地址。
- dev/test/pre/prod 不共享默认地址。
- Secret 只从环境或 CI Secret 获取。
- 禁止代码中出现生产数据库密码和管理员 Token。
- 生产环境执行需要显式开关，例如 `ALLOW_PROD_TESTS=true`。
- 日志和 Allure 附件必须脱敏。

## 13. 迁移步骤

### 阶段 0：恢复绿色基线

1. 删除已经修复的 4 条旧 xfail。
2. 确认 165 条远程用例全部通过。
3. 固化 Case ID 清单，作为迁移覆盖基线。

### 阶段 1：建立纯 pytest 骨架

1. 调整 `AGENTS.md`，允许纯 pytest 五层模式。
2. 建立 models、repositories、services、fixtures、tests。
3. 建立统一 `RepositoryResult`。
4. 建立 Secret 和多协议地址配置。

### 阶段 2：迁移两个参考业务域

1. `products`：展示参数化、边界值、Entity 和 Repository。
2. `cross_protocol`：展示 Service 编排和多协议一致性。

迁移完成后，同 ID 的旧 BDD 绑定从 `pytest_api` 删除。

### 阶段 3：按域迁移全部用例

建议顺序：

1. auth、test_runs。
2. products、orders。
3. claims、reviews。
4. faults、webhooks。
5. HTTP Lab。
6. SSE、WebSocket、MCP、gRPC。
7. 跨协议业务链路。

### 阶段 4：删除旧 BDD 实现

- 删除 `features/`。
- 删除 `steps/`。
- 删除 `FunctionalCaseExecutor`。
- 删除 `FunctionalCaseResult.checks`。
- 项目内不再导入 `pytest_bdd`。

### 阶段 5：大型项目门禁

- Ruff/格式化。
- mypy 或 pyright。
- pytest collection 和 Case ID 唯一性检查。
- `pytest -n auto`。
- 覆盖率阈值。
- Allure 历史趋势。
- 慢用例、隔离用例、xfail 的治理规则。

## 14. 验收标准

- 项目内没有 `.feature` 和 `pytest_bdd` 导入。
- 165 个 FTAPI ID 全部保留并通过。
- 删除 600+ 行集中执行器。
- 测试和 Service 不访问协议客户端私有字段。
- Repository 按业务域拆分。
- 核心请求和响应使用 Pydantic 强类型模型。
- 参数化覆盖合法、边界和非法等价类。
- 仓库中没有真实 Secret。
- 串行和 `-n auto` 结果一致。
- 单业务域可以由独立小组维护，不需要修改中央路由文件。

## 15. 主要风险

- 纯 pytest 与现有全局 Feature 强制规范冲突，必须先修改规范。
- 一次性删除 BDD 文件容易丢失 Case ID，应逐域迁移并做清单核对。
- 过度设计 Entity/Builder 会增加简单接口成本，只对核心业务对象强类型化。
- 参数化不应合并业务语义不同的 Case，否则报告难以追溯。
- 并行执行需要持续验证服务端 Test Run 隔离和异步事件隔离。

## 16. 改造完成后的适用范围

完成本方案后，`pytest_api` 适合：

- 测试开发和研发主导的自动化团队。
- 复杂业务依赖和跨协议流程。
- 需要强类型重构和大规模参数化的项目。
- 1000～5000 条 API/协议自动化用例。
- 多团队按业务域并行开发。
