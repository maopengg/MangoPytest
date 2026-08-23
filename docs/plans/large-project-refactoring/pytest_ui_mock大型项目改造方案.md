# pytest_ui 大型项目改造方案

## 实施结果（2026-08-23）

本方案已完成工程改造，当前实现采用与目标等价、且更贴合能力页面的目录命名：

- 493 条能力基线完整保留，并新增 4 条真实业务流和 3 条架构守卫，共收集 500 条。
- 260 个元素已从 JSON 迁移到项目独立的 5 个本地 Excel：`common`、`components`、`business`、`streams`、`protocols`。
- 通用执行器已拆到 `capabilities/`，`page_object/case_page.py` 只保留兼容适配。
- orders、claims、reviews 已具备独立 Entity、Spec、Factory、Repository、Page Object 和 Flow。
- 业务测试直接使用 pytest Fixture/Flow，不再经统一 JSON Case ID 执行。
- 固定数量校验已替换为唯一性、引用完整性和 inventory 一致性校验。
- 旧的不可达测试、`collect_ignore` 和重复 Page Object 已删除。
- 浏览器 Context、Test Run、下载目录和失败产物均按测试/worker 隔离；失败时保存截图、HTML、console 和 Trace。
- 已使用 `.venv`、远程 Mango Mock、Chromium 无头模式和 2 个 xdist worker 连续完成 3 轮全量回归，每轮 500 条全部通过。

原方案中的 `orders.xlsx`、`claims.xlsx`、`reviews.xlsx` 最终合并为 `business.xlsx`；协议演示元素独立为 `streams.xlsx` 和 `protocols.xlsx`，避免业务工作簿混入框架能力页面。

## 1. 项目定位

`pytest_ui` 定位为面向测试开发和研发团队的纯 pytest UI 自动化项目，强调：

- Python 原生测试、Fixture 组合和强类型参数化。
- 按业务域组织页面对象、业务 Flow 和测试数据。
- 使用 `mangoautomation.uidrives` 统一执行同步 Web 操作。
- 元素信息只读取项目自己的本地 Excel，不依赖飞书。
- 前置数据由本项目 Data Factory 创建，测试结束自动清理。
- 能够并行执行、失败重跑并生成可诊断的测试产物。

该项目不是 `simple_ui` 的 JSON/Excel Case 复制版。两者定位应当区分：

| 项目 | 用例入口 | 主要用途 |
|---|---|---|
| `simple_ui` | Excel Case | 演示数据驱动和完整操作能力 |
| `pytest_ui` | Python 测试函数 | 大型业务 UI 自动化和技术团队维护 |

## 2. 规范前提

当前项目级 `AGENTS.md` 固定使用 Feature → Steps 五层架构。纯 pytest UI 项目实施前，需要把规范调整为“按项目类型选择架构”：

- BDD UI：Feature → Steps → Flow/Factory → Page/Repository → Runtime。
- pytest UI：Tests → Flow → Factory → Page/Repository → Runtime。

纯 pytest 项目不应为了形式符合规范而增加空 Feature 和转发 Step。

## 3. 当前基线

- 103 条 `mangoautomation` 操作能力用例。
- 130 条交互元素用例。
- 260 条元素定位用例。
- 共 493 条，远程 Mango Mock 无头执行全部通过。
- 已有独立 Repository、Data Factory、元素仓库和自动清理机制。

改造期间必须保持 493 条基线持续通过，不允许通过删除或 `xfail` 降低覆盖。

## 4. 当前主要问题

### P0：统一 Page Object 职责过多

`page_object/case_page.py` 同时负责导航、操作分发、参数转换、数据准备、页面交互、断言和清理。继续增加页面后会成为多人修改冲突点。

### P0：旧测试被配置排除

`test_cases/conftest.py` 使用 `collect_ignore` 排除了 alert、click、input、navigation 等旧测试文件。必须明确这些用例是迁移、合并还是删除，不能长期保留“文件存在但不执行”的状态。

### P1：用例和元素数量写死

Loader 固定要求 103/130/260，元素仓库固定要求 260。新增用例或元素会直接导致收集失败。

### P1：业务用例仍由统一 JSON 执行器驱动

JSON 适合保存操作能力矩阵，但不适合承载大型项目的全部业务用例。业务目标、Fixture 依赖、marks 和断言应直接体现在 Python 测试中。

### P1：Data Factory 无法表达复杂场景

当前 Factory 只保存单个 `order_id`、`claim_id` 和 `review_id`，不能自然支持多个同类实体、实体关系、批量数据和组合状态。

### P1：断言偏操作能力验证

部分用例只验证元素仍存在或方法有返回值，能够证明操作被调用，但不能充分证明业务结果正确。

### P2：并行与失败诊断不足

尚未验证 xdist 并行隔离；截图、下载和 Allure 产物可能发生路径冲突；失败时缺少 Trace、页面截图、DOM、控制台日志和网络失败附件。

## 5. 目标五层架构

```text
L5  tests/                    纯 pytest 测试、marks、参数化、业务断言
 ↓
L4  flows/                    跨页面业务流程，不依赖 pytest
 ↓
L3  data_factory/             entities/specs/factories/scenarios
 ↓
L2  page_objects/             页面和组件操作
     repositories/            API/数据库前置数据访问
     elements/                本地 Excel 元素仓库
 ↓
L1  mangoautomation runtime   SyncWebRuntime、Context、Page
     common/mango_mock/       公共底层协议客户端
```

依赖只能向下：

- 测试不得直接操作 `Page`、HTTP Client 或数据库 Session。
- Flow 不得创建浏览器和测试数据客户端。
- Page Object 不负责创建业务数据，也不包含 pytest 断言。
- Factory 不操作页面。
- Repository 不编写 pytest 断言。

## 6. 目标目录

```text
auto_tests/ui/pytest_ui/
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
│   ├── components/
│   ├── orders/
│   ├── claims/
│   ├── reviews/
│   └── common/
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
├── fixtures/
│   ├── runtime.py
│   ├── browser.py
│   ├── pages.py
│   ├── factories.py
│   └── flows.py
├── tests/
│   ├── capabilities/          # 保留 103/130/260 能力基线
│   ├── auth/
│   ├── orders/
│   ├── claims/
│   └── reviews/
├── conftest.py
└── pytest.ini
```

## 7. 元素仓库标准

元素源只使用本地 Excel，并按业务模块拆分，避免一个超大工作簿成为冲突热点。

建议字段：

| 字段 | 说明 |
|---|---|
| `element_key` | 项目内稳定且唯一的业务键 |
| `page_key` | 页面或组件标识 |
| `name` | 中文名称 |
| `locator_type` | `test_id/css/role/text/xpath` |
| `expression` | 定位表达式 |
| `index` | 可选索引 |
| `description` | 使用说明 |
| `enabled` | 是否参与检查 |

加载阶段校验：

- `element_key` 全项目唯一。
- 定位方式属于允许集合。
- 必填字段完整。
- 测试引用的元素必须存在。
- 禁止固定元素总数。
- 优先使用 `data-testid`、role 和 label，XPath 仅作为最后方案。

Excel 只负责元素定义，不在单元格中保存可执行 Python 代码。

## 8. Page Object 和组件标准

Page Object 只封装页面行为和状态读取：

```python
class OrderPage:
    def __init__(self, base_data: BaseData, elements: ElementRegistry):
        self._base_data = base_data
        self._elements = elements

    def open(self) -> None:
        self._base_data.page.goto(self.url)

    def pay(self, order_id: int) -> None:
        self.order_id_input.input(str(order_id))
        self.pay_button.click()

    def status(self) -> str:
        return self.order_status.text()
```

要求：

- 单文件建议不超过 300 行。
- 公共 Header、Modal、Toast、Table 拆成 Component Object。
- 不在 Page Object 中调用 Data Factory。
- 不在 Page Object 中使用 `assert` 判断业务结果。
- 等待封装为明确状态，禁止业务测试直接 `sleep`。

## 9. Flow 标准

Flow 负责跨页面业务编排：

```python
class OrderFlow:
    def __init__(self, login_page, order_page):
        self.login_page = login_page
        self.order_page = order_page

    def pay_order_as(self, order_id: int, role: str) -> str:
        self.login_page.login_as(role)
        self.order_page.open()
        self.order_page.pay(order_id)
        return self.order_page.status()
```

Flow 返回可断言的结果或状态对象，不返回 Playwright Locator。

## 10. Data Factory 标准

每个核心业务域至少包含 Entity、Spec、Factory 和 Repository：

```python
@dataclass(frozen=True)
class OrderScenario:
    order: OrderData
    owner: UserData


class OrderFactory:
    def create(self, spec: OrderSpec | None = None) -> OrderData:
        payload = (spec or OrderSpec.pending()).build_payload()
        return self.repository.create(payload)
```

要求：

- 测试数据以 `AUTO_` 开头。
- Factory 可以创建多个同类型实体，不保存单个全局 ID。
- Scenario Factory 负责组合多个实体。
- Fixture 注册所有已创建资源，按 Test Run 或资源栈自动清理。
- 测试和 Page Object 中不写数据清理逻辑。

## 11. pytest 测试标准

业务测试使用明确的 Python 测试函数：

```python
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.order
@allure.id("PYUI-ORDER-001")
def test_manager_can_pay_pending_order(pending_order, order_flow):
    status = order_flow.pay_order_as(pending_order.id, role="employee")
    assert status == "paid"
```

要求：

- 一个测试验证一个业务目标。
- 测试 ID 稳定且唯一。
- 使用领域 marks 支持选择性回归。
- 正向、负向、权限和边界用例分别标记。
- 能力矩阵继续保留，但与业务测试分目录。
- 不再使用一个 JSON 文件承载所有业务场景。

## 12. Fixture 生命周期

| Scope | 内容 |
|---|---|
| session | `SyncWebRuntime`、只读元素注册表 |
| worker | xdist Worker 标识、独立产物目录 |
| function | Browser Context、Page、Test Run、Data Factory、Flow |

每条测试必须拥有独立 Browser Context 和 Test Run。失败、跳过和 Fixture 初始化异常都必须进入清理路径。

## 13. 失败产物标准

失败时自动保存：

- 当前页面截图。
- Playwright Trace。
- 当前 URL 和页面标题。
- 浏览器控制台 error。
- 网络请求失败摘要。
- 脱敏后的测试数据和 Test Run ID。
- 必要时保存 DOM，但必须过滤 Token、Cookie 和密码。

产物目录必须包含 Worker ID 和测试 Node ID，支持并行执行而不覆盖。

## 14. 迁移步骤

### 阶段 0：冻结基线

1. 保持 493 条全部通过。
2. 建立用例 ID、元素引用和收集数量检查。
3. 列出当前被 `collect_ignore` 排除的测试，逐条确定迁移或删除。

### 阶段 1：建立基础设施

1. 建立拆分后的本地 Excel 元素仓库和 Schema 校验。
2. 建立失败截图、Trace、控制台和网络附件 Hook。
3. 建立按 Worker 隔离的下载、截图和 Allure 目录。
4. 将固定数量检查改为唯一性和引用完整性检查。

### 阶段 2：拆分操作能力执行器

1. 把通用方法映射抽到 `capabilities/operation_dispatcher.py`。
2. 按组件、浏览器、断言、存储、窗口拆分能力测试。
3. 保持 103/130/260 基线 ID 不变。

### 阶段 3：按业务域迁移

依次迁移：

1. auth 和 Test Run。
2. orders。
3. claims。
4. reviews。
5. SSE、WebSocket 和其他协议页面。

每迁移一个域，就删除 `case_page.py` 中对应的前置数据和分支，不保留双实现。

### 阶段 4：大型项目执行治理

1. 验证 `pytest -n auto` 并行执行。
2. 建立 smoke、业务域、优先级和变更影响回归集。
3. 增加 Ruff、类型检查、collection 和 Excel Schema 门禁。
4. Allure 保留历史趋势，失败重跑不覆盖首次失败证据。

## 15. 验收标准

- 493 条基线用例全部保留并通过。
- 不再使用 `collect_ignore` 隐藏仍有效的测试。
- 业务测试不通过统一 JSON Case ID 执行器运行。
- `case_page.py` 被拆除或仅保留小型兼容适配器。
- 页面对象按业务域拆分，单文件建议不超过 300 行。
- 元素只读取本项目本地 Excel，不依赖飞书。
- 每个业务域有独立 Entity、Spec、Factory、Repository 和 Flow。
- 测试、Flow、Page、Factory、Repository 依赖方向符合五层架构。
- 负向用例可以断言真实错误，不被 Repository 的成功断言拦截。
- `pytest -n auto` 连续执行至少 3 次无数据和产物冲突。
- 失败报告包含截图、Trace、控制台日志和必要的脱敏上下文。

## 16. 预期收益

- Python 重构和 IDE 支持更好。
- 新增页面和业务域不会继续扩大统一执行器。
- 多人可以按业务目录并行开发，降低代码冲突。
- 数据准备、UI 操作和断言职责清晰。
- 大规模并行执行和失败定位能力可控。
