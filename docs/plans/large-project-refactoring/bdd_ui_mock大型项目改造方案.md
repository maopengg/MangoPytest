# bdd_ui 大型项目改造方案

## 实施结果（2026-08-23）

本方案已完成工程改造，结果如下：

- 493 条能力基线迁入 `features/capabilities/`，新增 4 条真实中文业务场景和 3 条架构守卫，共收集 500 条。
- orders、claims、reviews 均已具备真实 Feature、领域 Steps、类型化 Context、Flow、Factory、Repository 和 Page Object。
- 业务 Feature 不再通过 `UI-xxx` 编号转发；Case ID 矩阵仅保留在带 `@capability` 的框架能力区。
- 260 个元素只读取本项目 5 个本地 Excel，不再依赖 JSON 元素表或飞书。
- `pytest.ini` 已恢复标准 `test_*.py` 收集；旧的不可达绑定、Steps、Page Object、SQLAlchemy 配置和 Cleanup Hook 已删除。
- Factory 支持同类多实体，Test Run/Repository 负责统一清理；关键业务场景同时断言 UI 与 API 最终状态。
- 浏览器 Context、Test Run、下载目录和失败产物按测试/worker 隔离；失败时保存截图、HTML、console 和 Trace。
- 已使用 `.venv`、远程 Mango Mock、Chromium 无头模式和 2 个 xdist worker 连续完成 3 轮全量回归，每轮 500 条全部通过。

工作簿按页面能力拆分为 `common`、`components`、`business`、`streams`、`protocols`；相比按三个业务域各建一个工作簿，更适合当前 Mango Mock 同时承担业务和协议能力演示的页面结构。

## 1. 项目定位

`bdd_ui` 定位为面向产品、测试和开发共同评审的大型中文 BDD UI 自动化项目。

项目核心价值不是给 pytest 用例套一层 Feature，而是让 Feature 独立表达业务行为：

- Feature 描述用户角色、业务前置、页面行为和可观察结果。
- Steps 只负责翻译业务语言和维护场景上下文。
- Flow 负责跨页面业务编排。
- Data Factory 负责创建独立前置数据。
- Page Object 负责页面行为和状态读取。
- Repository 负责 API 或数据库数据访问和自动清理。
- 元素信息只读取本项目自己的本地 Excel，不依赖飞书。

## 2. 当前基线

- 103 条 `mangoautomation` 操作能力场景。
- 130 条交互元素场景。
- 260 条元素定位场景。
- 共 493 条，远程 Mango Mock 无头执行全部通过。
- 已有独立 Repository、Data Factory 和 cleanup token 清理机制。

改造期间必须保持这 493 条能力基线，不允许通过删除、跳过或长期 `xfail` 降低覆盖率。

## 3. 当前主要问题

### P0：Feature 只是 Case ID 转发层

当前主要步骤形式为：

```gherkin
当 操作交互控件用例 "UI-EL-001"
那么 BDD UI 用例应该执行成功
```

实际业务行为隐藏在 JSON 和统一执行器中。业务人员无法从 Feature 判断点击了什么、为什么点击以及预期结果是什么。

### P0：pytest 配置只收集一个绑定文件

当前 `python_files = test_mango_mock_bdd.py`，目录中的 alert、click、input、navigation 等旧 BDD 测试不会执行。必须完成迁移决策，不能长期保留不可达代码。

### P1：Steps 没有按业务域组织

新版通用 Step 根据 case ID 路由全部场景。大型团队会再次形成集中修改热点，Step 也无法被业务 Feature 自然复用。

### P1：统一 Page Object 职责过多

`page_object/case_page.py` 同时包含操作分发、页面导航、数据准备、业务等待、断言和清理，违反单一职责。

### P1：数据工厂层不完整

`actions/`、`specs/` 仍为空，Factory 只能保存单个订单、报销和评审 ID，不能表达复杂场景关系。

### P1：配置和遗留数据库代码混杂

当前配置仍初始化未使用的 SQLAlchemy Engine，并静默吞掉异常；旧 Repository 和 Cleanup Hook 与新版 Test Run 清理并存。

### P2：场景可追溯性和诊断不足

Feature 缺少稳定业务 ID、领域 Tag、明确步骤和业务断言；失败时缺少 Trace、截图、控制台及网络错误附件。

## 4. 目标五层架构

```text
L5  features/                 中文 Gherkin、业务 Tag、稳定 Case ID
 ↓
L4  steps/                    领域步骤、公共步骤、断言步骤
 ↓
L3  flows/                    跨页面业务编排
     data_factory/            entities/specs/factories/scenarios
 ↓
L2  page_objects/             页面和组件行为
     repositories/            前置数据访问和生命周期
     elements/                本地 Excel 元素仓库
 ↓
L1  mangoautomation runtime   SyncWebRuntime、Context、Page
     common/mango_mock/       公共协议客户端
```

固定依赖方向：

```text
Feature → Steps → Flow/Factory → Page/Repository → Runtime/Protocol
```

禁止：

- Feature 使用无业务含义的通用 Case ID 转发步骤。
- Step 直接创建 Playwright Page、HTTP Client 或数据库 Session。
- Page Object 创建测试数据或编写 pytest 断言。
- Factory 操作页面。
- Repository 在所有请求上强制成功断言。

## 5. 目标目录

```text
auto_tests/ui/bdd_ui/
├── config/
│   ├── settings.py
│   └── environments/
├── elements/
│   ├── excel_loader.py
│   ├── registry.py
│   └── workbooks/
│       ├── common.xlsx
│       ├── components.xlsx
│       ├── orders.xlsx
│       ├── claims.xlsx
│       └── reviews.xlsx
├── page_objects/
│   ├── common/
│   ├── components/
│   ├── orders/
│   ├── claims/
│   └── reviews/
├── flows/
│   ├── authentication_flow.py
│   ├── order_flow.py
│   ├── claim_flow.py
│   └── review_flow.py
├── data_factory/
│   ├── entities/
│   ├── specs/
│   ├── factories/
│   └── scenarios/
├── repositories/
│   ├── test_run_repository.py
│   ├── auth_repository.py
│   ├── order_repository.py
│   ├── claim_repository.py
│   └── review_repository.py
├── steps/
│   ├── common/
│   ├── auth/
│   ├── orders/
│   ├── claims/
│   ├── reviews/
│   └── assertions/
├── features/
│   ├── capabilities/          # 保留 103/130/260 能力基线
│   ├── auth/
│   ├── orders/
│   ├── claims/
│   └── reviews/
├── test_cases/                # Feature 绑定与 marks
├── fixtures/
├── hooks/
├── conftest.py
└── pytest.ini
```

## 6. 标准业务 Feature

Feature 必须直接表达业务，不以执行器编号替代行为：

```gherkin
# language: zh-CN
@ui @order
功能: 订单支付

  背景:
    假如 已创建隔离测试运行

  @smoke @positive
  场景: BDD-UI-ORDER-001 员工支付待支付订单
    假如 存在一个属于当前员工的待支付订单
    并且 员工已经登录 Mango Mock
    当 员工在订单页面支付该订单
    那么 页面订单状态应该为 "paid"
    并且 API 查询到的订单状态应该为 "paid"
```

负向场景示例：

```gherkin
  @negative @permission
  场景: BDD-UI-ORDER-002 未登录用户不能支付订单
    假如 存在一个待支付订单
    并且 当前浏览器没有登录状态
    当 用户尝试支付该订单
    那么 页面应该提示 "请先登录"
    并且 API 查询到的订单状态应该为 "pending"
```

要求：

- 每个场景只有一个清晰业务目标。
- 至少断言页面结果；关键业务场景增加 API 或数据库最终状态断言。
- Feature 不出现 URL、CSS、XPath、HTTP 请求代码或数据库字段实现。
- 场景 ID 稳定且唯一。

## 7. Steps 标准

Steps 按业务域拆分，只做参数解析、调用和上下文传递：

```python
@given("存在一个属于当前员工的待支付订单")
def pending_order(order_scenario_factory, scenario_context):
    scenario_context.order = order_scenario_factory.pending_for_employee()


@when("员工在订单页面支付该订单")
def pay_order(order_flow, scenario_context):
    scenario_context.actual_status = order_flow.pay(scenario_context.order.id)


@then(parsers.parse('页面订单状态应该为 "{expected}"'))
def assert_order_status(expected, scenario_context):
    assert scenario_context.actual_status == expected
```

要求：

- 不使用一个 `scenario_context: dict` 保存无约束键，按业务域建立类型化 Context。
- Step 不直接查 Excel 元素。
- Step 不调用 Playwright Locator。
- 公共断言放在 `steps/assertions/`，领域断言保留业务名称。
- 禁止新增“执行用例 ID”式通用 Step。

## 8. 元素仓库标准

元素只从本项目本地 Excel 读取，并按页面或业务域拆分工作簿。

Loader 在测试收集阶段完成：

- 元素键唯一性校验。
- 必填字段和定位类型校验。
- Feature/Page Object 引用完整性校验。
- 重复定位器提示。
- 禁止固定元素总数。

Page Object 只通过稳定 `element_key` 查询元素，不在 Python 文件中复制 XPath 和 CSS。

## 9. Page Object 与 Flow 标准

Page Object 只提供页面原子行为：

```python
class OrderPage:
    def pay(self, order_id: int) -> None: ...
    def status(self) -> str: ...
    def error_message(self) -> str: ...
```

Flow 负责跨页面编排：

```python
class OrderFlow:
    def pay(self, order_id: int) -> str:
        self.navigation.open_orders()
        self.order_page.pay(order_id)
        return self.order_page.status()
```

页面对象单文件建议不超过 300 行，Header、Modal、Toast、Table 等复用结构拆成 Component Object。

## 10. Data Factory 标准

数据工厂完整实现：

```text
data_factory/
├── entities/      强类型业务对象
├── specs/         pending/paid/refunded/invalid 等规格
├── factories/     单实体创建
└── scenarios/     用户、角色和多个实体的组合场景
```

要求：

- 数据名称以 `AUTO_` 开头。
- Factory 返回实体，不在自身保存单个可覆盖 ID。
- 一个场景可以同时创建多个订单、用户和关联对象。
- Test Run 是默认隔离和清理边界。
- Fixture 无论测试通过、失败还是跳过都执行清理。
- 测试数据通过 Factory/Repository 创建，不在 Step 中直接调用 API。

## 11. 能力 Feature 与业务 Feature 分离

103/130/260 条能力场景仍有价值，但应单独放入 `features/capabilities/`：

- 用于验证 `mangoautomation` 方法和 Mango Mock 元素契约。
- 可以由矩阵生成 Scenario Outline。
- 不把能力场景当成业务场景统计。
- 业务 Feature 不引用 `UI-OP-xxx` 或 `UI-EL-xxx` 执行器。

报告中分别展示：

- Framework capability coverage。
- Business scenario coverage。
- Element contract coverage。

## 12. Fixture 与场景上下文

| Scope | 内容 |
|---|---|
| session | `SyncWebRuntime`、只读元素注册表 |
| worker | xdist Worker 标识、独立产物目录 |
| function | Context、Page、Test Run、Factory、Flow、Scenario Context |

建议为每个业务域提供类型化上下文：

```python
@dataclass
class OrderScenarioContext:
    order: OrderData | None = None
    actual_status: str | None = None
    response: RepositoryResult | None = None
```

## 13. Hooks 和测试产物

失败 Hook 自动附加：

- 页面截图。
- Playwright Trace。
- 当前 Feature、Scenario、Step 和业务 Context。
- 当前 URL、标题和浏览器控制台错误。
- 网络请求失败摘要。
- 脱敏后的 Test Run ID 和业务实体 ID。

产物按 Worker ID、Feature、Scenario 分目录，确保并行执行不覆盖。

## 14. 配置治理

- 删除未使用的 SQLAlchemy 初始化、旧 Repository 和空清理 Hook。
- dev/test/pre/prod 地址独立，禁止测试环境默认回退生产环境。
- 账号、密码、Token 和 Cookie 由环境变量或 CI Secret 注入。
- 日志和 Allure 附件统一脱敏。
- 浏览器类型、无头模式、Trace、视频和并行参数均可配置。

## 15. 迁移步骤

### 阶段 0：冻结和清点基线

1. 保持 493 条能力场景全部通过。
2. 清点当前未被 `pytest.ini` 收集的旧 Feature 和测试绑定。
3. 将每个旧场景标记为迁移、合并或删除，并留下评审记录。
4. 增加 Feature 场景 ID 唯一性和绑定完整性检查。

### 阶段 1：建立标准业务切片

选择订单支付作为第一个完整切片，建立：

1. 本地 Excel 元素。
2. Order Page Object。
3. Order Entity、Spec、Factory 和 Repository。
4. Order Flow。
5. 真实中文 Feature 和领域 Steps。
6. UI 状态与 API 最终状态双重断言。

### 阶段 2：拆分能力验证

1. 将 103/130/260 移入 `features/capabilities/`。
2. 把统一操作分发从业务 Page Object 中移出。
3. 能力测试和业务测试使用不同 Allure Feature/Suite。

### 阶段 3：按业务域迁移

依次迁移：

1. auth 和 Test Run。
2. orders。
3. claims。
4. reviews。
5. SSE、WebSocket 和其他协议页面。

每迁移一个域，删除 `case_page.py` 和通用 Steps 中对应分支。

### 阶段 4：清理遗留实现

1. 删除旧的不可达测试绑定和 Steps。
2. 删除未使用 SQLAlchemy 配置和空数据层目录。
3. 删除“执行 Case ID”通用业务 Step。
4. `pytest.ini` 恢复标准 `test_*.py` 收集，并增加收集门禁。

### 阶段 5：大型项目门禁

1. Ruff、类型检查和 Feature 格式检查。
2. 本地 Excel Schema 和引用完整性检查。
3. `pytest -n auto` 并行回归。
4. smoke、领域、优先级和变更影响测试集。
5. Allure 历史趋势、失败归类和 flaky 用例治理。

## 16. 验收标准

- 493 条能力基线全部保留并通过。
- `pytest.ini` 不再只收集单个绑定文件。
- 不存在仍有效但无法被收集的 Feature 或测试文件。
- 业务 Feature 不再出现“执行 UI-xxx 用例”通用步骤。
- 每个核心业务域都有 Feature、Steps、Flow、Factory、Repository 和 Page Object。
- 元素只读取本项目本地 Excel，不依赖飞书。
- Factory 可以创建多个同类实体，且所有数据自动清理。
- Page Object 不包含 Data Factory 调用和 pytest 断言。
- 关键场景同时验证 UI 状态与 API/数据库最终状态。
- `pytest -n auto` 连续执行至少 3 次无数据、截图和报告冲突。
- 失败报告包含截图、Trace、控制台和网络错误上下文。

## 17. 预期收益

- Feature 真正成为可评审、可追溯的业务规范。
- Steps 可以按领域复用，不再依赖编号分支。
- 页面、数据和业务流程职责清晰。
- 产品、测试和研发能够使用同一套业务语言沟通。
- 支持多团队按业务域并行开发和大规模回归。
