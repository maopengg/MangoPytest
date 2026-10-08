# AI 元素定位接入方案

> 状态：**阶段 0–5 已实施**（见文末「实施结果与偏差」）
> 适用版本：`mangoautomation 2.1.0` + `playwright 1.62.0`
> 范围：`mango_pytest` 全部 UI 项目（`simple_ui` / `bdd_ui` / `pytest_ui`）

---

## 0. 结论摘要

本项目的 AI 元素定位**接线已完成约七成**：配置面、提示词传递链、引擎装配、结果可观测钩子都已存在且可用。**真正的阻塞不在代码，而在两件事**：

1. **合规**：`AI_API_KEY` 目前是控制台明文输入框，且 `runtime_overrides` 原文写入 SQLite 并在页面回显，直接违反 `AGENTS.md`「真实 API Key 禁止入库」。
2. **数据**：元素工作簿 260/260 行的 `AI定位提示词1` 全是模板串 `查找元素：<元素名>`，slot2/slot3 全空。**提示词列填充率 100%，信息量为零**，AI 拿到的描述不比 `name` 多一个字节。

因此本方案把「补数据」和「修合规」放在开发之前，代码改动集中在「补齐元素元数据」和「可观测性」两块。

**已证实的关键约束（影响方案设计）**：

| 约束 | 影响 |
|---|---|
| `_heal_mode()` 在 2.1.0 硬编码 `return 2` | `ELEMENT_HEALING_MODE` 是**死配置**；没有"只建议不执行"的观察档；一旦开 AI，命中即临时自愈并**改变用例结果** |
| `first_prompt()` 只取**第一个**非空 prompt | 元素表 3 组提示词列，对 AI 实际**只有第 1 组有效**；slot2/3 仅参与语义校验 |
| `PromptTextCandidateSource` 未注册 | 提示词**不会**自动变成 TEXT 定位候选 |
| 无模型响应缓存（`CACHE_TTL=60` 只缓存历史自愈记忆） | TTL 内重复触发仍会**真实调用模型** |
| 提示词 YAML 不可外部覆盖 | 想改提示词模板只能提上游需求，或改包内文件后重装 |
| `AgentCircuitBreaker` 是进程级类变量 | 跨用例共享，需明确隔离语义 |

---

## 1. 目标与非目标

### 1.1 目标

1. 当元素的固定定位器失效时，能借助 AI 基于「中文业务描述 + 页面无障碍快照」重新定位到正确元素，让用例继续执行。
2. 支持「只有描述、没有固定定位器」的元素（描述即定位）。
3. **元素维护者能在元素表里直接填写 AI 提示词**，且填写体验友好：有明确规范、有正反例、写下去真的被 AI 读到、写错会被体检拦住（详见 §3.4）。
4. AI 的使用**可开关、可观测、可计成本、可审计**，默认不对全量用例生效。
5. 真实 API Key 不入库、不回显，符合 `AGENTS.md`。

### 1.2 非目标

1. **不做**自愈结果回写 Excel / 飞书（当前全仓库无此能力，且需要元素表写接口，属于独立课题）。
2. **不做**视觉兜底（`WebVisualLocatorAgent`）。它要求绕过 `standalone()` 直接构造 harness 并额外接一个多模态 `vision_model_client`，建议作为二期独立评估。
3. **不做** `mangoautomation.step_healing`（页面步骤级自愈）。该子系统在 2.1.0 中无任何运行时调用点，属未启用能力，留待 Flow 层演进时再评估。
4. **不引入**新框架、新依赖；不改变现有五层架构与 `core/ui/` 的公共能力边界。
5. **不在** `simple_api` / `bdd_api` / `pytest_api` 中引入任何 AI 相关配置（纯 API 项目无元素定位概念）。

---

## 2. 现状基线

### 2.1 已经具备（直接复用，无需开发）

| 能力 | 位置 |
|---|---|
| 元素表 3 组 `AI定位提示词` 列定义 | `core/sources/element_schema.py:3-22` |
| 提示词 → `LocatorDefinition.prompt` → `ElementListModel.prompt` | `core/ui/element_runtime.py:84,96,144-147` |
| 8 个 AI/自愈配置项（系统级 + 运行级） | `core/settings/settings.py:25-32`、`core/ui/config.py:28-55` |
| 运行参数覆盖链路（控制台 → 子进程 env） | `auto_tests/project_registry.py:27-46` → `core/execution/catalog.py:55-97` → `web_console/run_service.py:56-71` → `core/execution/command_builder.py:56` |
| 引擎装配 | `core/ui/element_runtime.py:197-213` |
| 结果可观测字段 | `ElementResultModel.locator_engine`（`used_ai` / `used_source` / `temporary_heal_used` / `final_score` / `reject_reasons` / `heal_record_id`） |
| Allure 证据附件 | `core/ui/element_runtime.py:272-299`（操作信息/操作结果）、`:342`（`ai_prompt`） |
| 库内成本护栏 | 预算 5s+30s、候选上限 24（AI 占 5）、熔断 2 次/60s、单候选 2s |

**控制台已经会自动渲染 8 个 AI/自愈参数**（因为字段来自 `PROJECT_REGISTRY[...]["runtime_options"]`），无需额外开发即可开启。

### 2.2 缺口清单

#### A 类：阻塞项（不解决则 AI 无法有效工作）

| # | 缺口 | 位置 | 影响 |
|---|---|---|---|
| A1 | **无可用凭据** | 环境变量为空；三个项目 `.env.*` 均无 AI 项 | 全部后续工作无法验证 |
| A2 | **提示词数据无信息量** | `core/sources/workbooks/mock_ui/mock_ui_elements.xlsx` 260/260 行为 `查找元素：<元素名>` | AI 退化为"用元素名猜"，效果不可预期 |
| A3 | **Key 明文落库与回显** | `project_registry.py:38`（`type: "text"`）、`run_service.py:71`、`app.js:49` | 违反 `AGENTS.md`；凭据泄露风险 |

#### B 类：质量项（决定 AI 准不准）

| # | 缺口 | 位置 |
|---|---|---|
| B1 | `ElementModel` 的 `description_template` / `element_version` / `page_url` / `frame_path` / `collect_snapshot` **全部未填** | `core/ui/element_runtime.py:162-180` |
| B2 | **三列提示词只生效一列**：`first_prompt()` 只取第一个非空 `prompt`，slot2/slot3 对 AI 完全无效（仅 `semantic.py:82` 检测"动态元素"标记时遍历全部），界面与文档均未说明，用户会白填 | 库侧 `context/sanitizer.py:7-12` |
| B3 | `.env` 白名单不含 `AI_*`，写进 `.env.*` 不会反映到控制台预览 | `core/execution/catalog.py:101-104` |
| B4 | 控制台「元素自愈模式」1/2/3 下拉不产生行为差异 | `project_registry.py:39` + 库侧 `_heal_mode()` |
| B5 | **无提示词体检**：两个「语义反转」陷阱（`排除项` 不在行首、用 `\|` 拼接多列）与「`${{未定义变量}}` 硬失败」都无任何拦截 | 待新增 |
| B6 | `category` 直接送页面 key（`componentsPage`），语义弱 | 库侧 `agent/web/prompt.py:33` |
| B7 | `说明` 列 212/260 非空且有语义，但**只进 Allure 证据**，未作为描述回退入模型 | `core/ui/element_runtime.py:159` |

#### C 类：增强项

| # | 缺口 | 位置 |
|---|---|---|
| C1 | 只支持"固定定位优先"，不支持"纯描述元素" | `core/ui/element_runtime.py:150-151` 硬抛 `ValueError` |
| C2 | 可观测性只有单步 Allure 附件，无汇总、无用例级标记、无控制台面板 | — |
| C3 | 无端到端 AI 测试（只有参数透传断言） | `tests/test_ui_element_runtime.py:145-191` |
| C4 | 无 AI/自愈使用文档与提示词编写规范 | `docs/` |
| C5 | `WebBaseObject` 为死代码 | `core/ui/web_base.py:62-67` |

---

## 3. 总体设计

### 3.1 分层职责

沿用现有架构，不新增层。AI 能力作为 `core/ui/` 的公共基础设施存在，三个 UI 项目与 `auto_tests/common/mango_mock/` 通过既有装配点消费：

```
L5  Tests / Features          ← 只表达用例；不感知 AI
L4  Flows / Page Objects      ← 只表达业务动作；不感知 AI
L3  Data Factory              ← 不变
L2  Page Objects + 元素仓库    ← 元素定义与提示词在这里落库（Excel / 飞书）
L1  SyncWebRuntime            ← core/ui/element_runtime.py 装配 AI 引擎
     └─ mangoautomation 2.1.0（harness / healing / agent）
```

**原则**：AI 的开关、门禁、观测统一在 `core/` 与项目配置层实现，**禁止**在 Tests / Steps / Flows 里判断 `is_ai` 或写 AI 分支。

### 3.2 配置与优先级

统一沿用 pydantic-settings 的既有优先级（后写覆盖前写）：

```
1. core/settings/settings.py 默认值            ← 最低
2. 项目 .env.<env>（注：AI_* 目前不在控制台预览白名单内，见 B3）
3. 环境变量（CI Secret 注入）
4. Web Console runtime_overrides（写入子进程 env）  ← 最高
```

**新增约定**：
- `AI_API_KEY` **只允许**来自「环境变量 / CI Secret」。控制台不提供 Key 输入（或提供但打码且不落库），见阶段 0。
- 其余 `AI_*` 与 `ELEMENT_HEALING_*` 保留控制台可调，便于按运行调参。

### 3.3 触发与降级策略

复用库内既有触发逻辑（固定定位重试窗口耗尽后进入自愈，窗口默认 10s），**不自行实现重试或自愈**。

新增项目侧三点：

1. **显式降级标记**：区分三种状态并落日志与证据——
   - `AI 未启用`（`AI_ELEMENT_HEALING_ENABLED=false` 或 Key 为空）
   - `AI 启用但未命中`（`used_ai=true` 但最终失败）
   - `AI 成功自愈`（`used_ai=true` 且操作成功）

   现状是三者不可区分（降级完全靠 `api_key` 为空隐式发生）。

2. **按运行门禁**：通过 markers 控制生效范围（阶段 4），默认只在显式开启的运行中生效。

3. **熔断语义显式化**：`AgentCircuitBreaker` 是进程级类变量，跨用例共享。方案选 A：

   | 选项 | 语义 | 取舍 |
   |---|---|---|
   | **A（推荐）** | 整轮共享，不重置 | 与库设计一致，避免"每个用例都重试一遍失败模型"放大成本 |
   | B | 每用例重置（fixture 内 `reset()`） | 隔离性好，但同一坏元素会重复烧钱 |

### 3.4 数据契约：提示词规范（本节为方案核心）

AI 效果上限由提示词质量决定。以下规则**全部经代码实测验证**，不是推测。

#### 3.4.1 先纠正一个关键事实：AI 读的是 `elements[0].prompt`

库侧取描述的链路是（`element_healing/context/sanitizer.py:7-12` → `context/builder.py:40` → `agent/web/prompt.py:34`）：

```text
ElementListModel.prompt（elements 中第一个非空值，first_prompt）
        ↓
HealingContext.prompt
        ↓
AI 请求体 target.prompt        ← 文本 Agent 真正读到的"元素描述"
```

**`ElementModel.description_template` 不会进入文本 Agent 的 `target.prompt`。** 它只作用于三处：
`elements` 为空时的占位定位组合成（`_sync_element.py:88-98`）、视觉兜底
（`agent/visual/agent.py:195`）、变量追踪观测（`observability/recorder.py:98`）。

> 因此：**用户填的提示词必须最终落在 `elements[0].prompt` 上**。本方案阶段 2 的合并逻辑
> 就是为此而设。`description_template` 仍要设置（AI-only 与视觉路径需要），但**它不是**文本
> Agent 的描述来源。

#### 3.4.2 三列 = 三行结构（让 3 列全部生效）

元素表给了 3 组 `AI定位提示词` 列，但 `first_prompt()` **只取第一个非空值**，所以现状下
slot2/slot3 对 AI 完全无效（`semantic.py:82` 只在"动态元素"标记检测时遍历全部 slot）。

**方案：项目侧把 3 列合并为多行文本，写入 `elements[0].prompt`，`elements[i>0].prompt` 置空。**

三列的推荐语义（不改列名、不违反 18 列规范）：

| 列 | 语义 | 必填 |
|---|---|---|
| `AI定位提示词1` | 控件描述（控件种类 + 区分特征） | 是 |
| `AI定位提示词2` | 所在区域 / 上下文 | 否 |
| `AI定位提示词3` | 排除项（**必须以 `排除项：` 开头**） | 否 |

合并规则：`"\n".join(非空列)`。**必须用换行，禁止用 `|` 等分隔符拼接**（原因见 3.4.3 反例 ②）。

该设计同时向后兼容：用户只填第 1 列时，合并结果就等于第 1 列。

#### 3.4.3 六条填写规则（含两个已实证的语义反转陷阱）

| # | 规则 | 依据 |
|---|---|---|
| R1 | **`排除项：` 必须独占一行且在行首** | `positive_prompt()` 用 `^\s*排除项\s*[：:]` 做**行首**匹配；不在行首则**不会被剔除，反而变成正向必需文本**（语义反转） |
| R2 | **用中文引号 `「」`/`“”` 包裹 DOM 中真实存在的可见文案** | `_quoted_texts()` 抽取引号内容为最强目标文本；实测 `「选择文件」`→ 必需文本含 `选择文件` |
| R3 | **把最关键的点放在「的」之后** | `semantic_core_text()` 取最后一个「的」之后的片段作为核心文本；实测 `文件上传区域的文件选择框` → 必需文本 `文件选择框` |
| R4 | **不要把 `|` `-` `_` `/` `：` `>` 和空格当装饰分隔符** | `split_target_text()` / `semantic_required_texts()` 会按其切词，最后一段会变成必需文本 |
| R5 | **不要把"排除项"写进描述句中** | 同 R1，会成为正向目标 |
| R6 | **多行是官方支持的** | `positive_prompt()` 按行 `splitlines()` 处理，`\n` 是合法结构分隔符 |

**实测对照（同一元素的三种写法）**：

| 写法 | `positive_prompt` 结果 | `semantic_required_texts` 结果 | 判定 |
|---|---|---|---|
| 现状：`查找元素：ui-file-input` | 原样 | `['input']`（连字符切词后的残渣，无意义） | ❌ |
| **设计：3 行合并** `文件上传区域的文件选择框\n位于「组件演示」页的组件面板内\n排除项：下载按钮` | 前两行（排除项被正确剔除） | `['input', '组件演示', '组件面板内']` | ✅ |
| 反例①：排除项不在行首 `…的文件选择框，排除项：下载按钮` | 原样（未剔除） | `['input', '下载按钮']` | ❌ **排除项反转成必需文本** |
| 反例②：用 `\|` 拼接 3 列 | 原样（未剔除） | `['input', '组件演示', '下载按钮']` | ❌ **排除项反转** |

> 反例①②是**最危险的两个坑**：用户以为写了排除条件，实际却把它变成了必须命中的目标，会导致
> 候选被错误接受或拒绝。体检（4.1 阶段 1）必须把这两种写法列为**错误级**告警。

#### 3.4.4 提示词支持 `${{变量}}` 运行时替换（含硬失败风险）

`SyncElement.init_element()` 会对 `elements[i].prompt` 执行 `base_data.test_data.replace(...)`
（`_sync_element.py:349-351`），即提示词支持 mangotools 的 `${{变量}}` 语法，可写参数化描述
（如 `点击「${{button_text}}」按钮`）。

⚠️ **风险**：变量未被注入时 `replace_str` 会抛 `MangoToolsError`，导致**元素初始化直接失败**——
**即使 AI 关闭也会失败**，因为它发生在 `init_element()` 而非自愈链路内。因此：
- 体检必须扫描提示词中的 `${{...}}`，与运行期已注入变量比对，未定义即**错误级**告警；
- 仅在确定注入的场景使用变量，否则写静态描述。

#### 3.4.5 不新增元素表列

`AGENTS.md:113-115` 规定元素表固定 18 列，并明文禁止 iframe、等待、快照、交互状态等运行行为入表；
`tests/test_ui_element_runtime.py:118-130` 还有硬断言（`len == 18` 且
`{AI自愈状态, 采集快照, 等待时间, 是否iframe1}` 与表头不相交）。方案所需的模型字段全部可由现有列 +
代码派生得到：

| 想填的模型字段 | 需要加列？ | 来源 |
|---|---|---|
| AI 元素描述 | 否 | 三列提示词合并后写入 `elements[0].prompt` |
| `description_template` | 否 | 同上（供 AI-only 占位合成与视觉路径使用） |
| `element_version` | 否 | 定位器集合 **+ 提示词** 的哈希（**不可用 `ID` 冒充**：定位表达式或提示词变更时 ID 不变，会让观测 `base_locator_version` 失真） |
| `page_url` | 否 | 由 `页面名称`（页面 key，如 `componentsPage`）在代码中映射到路由；URL 随 dev/test/prod 变化，写进元素表必然出错，且站点为 hash 路由 |
| `collect_snapshot` | 🚫 禁止 | `AGENTS.md` 明文禁止"快照"入表；属运行策略，应在 settings |
| `frame_path` | 🚫 禁止 | `AGENTS.md` 明文禁止 iframe 入表 |
| AI-only（纯描述元素） | 否 | 用「定位列为空 + 提示词非空」隐式表达 |

> 如未来确需新增列，属**规范变更**，顺序为：改 `AGENTS.md:113-115` → 改
> `CANONICAL_ELEMENT_HEADERS` → 改测试断言 → 同步飞书 16→18 列映射
> （`core/sources/feishu/document_data.py:128-131`）→ 更新工作簿。

#### 3.4.6 两个尚未利用的免费语义来源

| 来源 | 现状 | 优化建议 |
|---|---|---|
| `页面名称` → `ElementModel.category` | **已经**会送进 AI 请求（`prompt.py:33`），但值是页面 key（`componentsPage`），语义弱 | 阶段 2 在代码里把页面 key 映射为中文页面名（如 `组件演示页`），零成本提升上下文质量 |
| `说明` 列 | 212/260 非空，内容有语义（如 `跳到主要内容`），但**只进 Allure 证据**，不入模型（`to_element_model()` 不引用它） | 作为 `AI定位提示词1` 为空时的**回退描述**；但需过滤超长噪声（实测有 160 字的页面抓取文本） |

### 3.5 可观测性

现状：`locator_engine` 字段已具备，但埋在一个「操作结果」JSON 附件里。

方案：提升为**独立 Allure 步骤 + 用例级标签**，并从 `model_dump()` 提取以下字段（均已在库侧 metadata 中）：

| 字段 | 用途 |
|---|---|
| `used_source` | `fixed_locator` / `ai_accessibility` / `ai_visual` / `candidate_exhausted` |
| `used_ai` | 是否真的调用了模型 |
| `temporary_heal_used` | 是否临时采用了自愈结果 |
| `final_score` | 候选得分 |
| `heal_record_id` | 自愈记录 ID（后续对接持久化用） |
| `reject_reasons` | 拒识原因（≤10 条） |
| `trace.model` / `prompt_version` / `schema_version` | 模型与提示词版本 |
| `trace.agent_circuit_breaker` | 熔断状态 |
| `trace.stages[]` | 各阶段耗时（memory / historical / DOM / agent / visual） |

另需在 `ElementRuntime` 层聚合每轮的 AI 统计（调用次数、成功次数、熔断次数），输出到运行级产物，供 Web Console 后续做面板。

### 3.6 安全与成本

| 项 | 措施 |
|---|---|
| Key 存储 | 只走环境变量 / CI Secret；控制台字段改 `password` 或移除；落库与回显打码 |
| Key 日志 | 禁止把 Key 写入日志或证据附件；`AI_BASE_URL` 可记录 |
| 调用成本 | 复用库内护栏（预算 5s+30s、候选 ≤24、熔断 2 次/60s）；项目侧增加**每轮调用次数上限**告警 |
| 误操作风险 | 默认不全局开启；按 marker / 按运行开启；`AI_SEMANTIC_STRENGTH` 保持 0（宽松）起步 |
| 效果验收 | 双跑对比（见 §6.2），不允许用"用例变绿"作为唯一成功标准 |

---

## 4. 分阶段实施计划

### 阶段 0：凭据与合规（阻塞项，必须先做）

**改动**
1. `auto_tests/project_registry.py`：`AI_API_KEY` 的 `type` 由 `text` 改为 `password`；或在方案 A 下直接**从 `UI_RUNTIME_OPTIONS` 移除**，只保留环境变量注入。
2. `web_console/run_service.py` / `repository.py`：落库前对 `runtime_overrides` 中的敏感键（`AI_API_KEY` 及未来的 `*_TOKEN` / `*_SECRET`）做**打码**（如 `sk-****abcd`）。
3. `web_console/static/app.js`：详情页回显时同样打码；`app.js:32` 增加 `password` 类型的渲染分支。
4. 清理已落库的历史明文 Key：迁移脚本或提示手动清理 `artifacts/temp/web_console/web_console.sqlite3`。
5. 凭据准备：确定 AI 网关与模型，按 CI Secret 注入 `AI_API_KEY`。

**验收**
- 控制台与数据库中都搜不到完整 Key（用 `sk-test-` 前缀做端到端验证）。
- `ENV=test AI_API_KEY=xxx ... python -c "from ... import MockUIConfig; MockUIConfig().AI_API_KEY"` 仍能正确读到（env 注入路径不被破坏）。
- 现有 `tests/test_web_console/test_execution.py:22-30` 与 `:94-119` 全绿。

**工作量**：0.5–1 人日

---

### 阶段 1：提示词数据规范化与填写体验（决定 AI 效果上限）

目标：**让维护者知道怎么写、写下去真的被 AI 看到、写错能被拦住。**

**改动**

1. **三列按 §3.4.2 结构回填** `core/sources/workbooks/mock_ui/mock_ui_elements.xlsx`：
   - `AI定位提示词1` = 控件描述（必填）
   - `AI定位提示词2` = 所在区域 / 上下文（可选）
   - `AI定位提示词3` = 排除项，**必须以 `排除项：` 开头**（可选）
   - 清除全部 260 行 `查找元素：<元素名>` 模板串
2. **把填写规范写进工作簿自带的 `说明` sheet**（该 sheet 已存在且有 9 行说明，第 6/8 行已在讲"元素行只保存 AI 定位提示词""每组…AI 提示词"，是最自然的落点）。需补充：
   - 三列语义、多行需 `Alt+Enter`、禁止用 `|` 拼接、`排除项：` 必须独占行首
   - 三个正例（`ui-file-input` / `nav-components` / `history-result`）与两个反例
3. **同步飞书源**：`core/sources/feishu/document_data.py:94` 的 `f"查找元素：{name}"` 兜底改为**留空**，否则飞书源会持续产出垃圾提示词；同时确认 16→18 列映射只填 slot1，避免 3.4.2 的合并逻辑拿到重复内容。
4. **新增提示词体检（lint）**，两层：
   - **加载期**：`core/sources/ui_elements.py` 在 `load_element_records()` 后调用体检。**错误级默认 fail fast**
     （避免"静默错误结果"流入测试），可通过配置开关降级为告警以应对紧急情况；警告级仅记日志。
   - **可独立执行的批量脚本**（供元素维护者在提交前跑），输出报告到 `artifacts/`。
   规则分级（依据均为 §3.4.3 实证）：

   | 级别 | 规则 |
   |---|---|
   | **错误** | 含 `排除项` 但**不在行首**（语义反转，反例①） |
   | **错误** | 多列内容用 `\|` 等分隔符拼接而非换行（语义反转，反例②） |
   | **错误** | 含 `${{变量}}`，但变量不在已注入集合内（会导致元素初始化**硬失败**，且与 AI 开关无关） |
   | **错误** | `排除项：` 是唯一内容（没有任何正向描述） |
   | **警告** | 与元素名等价（去掉 `查找元素：` 前缀、分隔符后相同） |
   | **警告** | 命中模板串模式 `^查找元素[：:]` |
   | **警告** | 长度 < 6 或 > 120 个字符 |
   | **警告** | 建议项缺失：未含可识别的控件种类/作用域关键词（库侧 `verification/target_intent.py` 的 `CONTROL_KINDS` / `SCOPE_KINDS`） |

5. **（可选但推荐）提示词起草助手**：用 `mangoautomation.element_healing.snapshot.AccessibilitySnapshotBuilder`
   抓取目标页面的无障碍快照，按纯规则（节点 role/name/text/label + 12 层祖先）生成「控件种类 + 可见文案（自动加中文引号）+ 所在区域」的初稿，人工润色后回填。**不需要调用模型**，成本为零，能显著降低撰写门槛。
6. **（可选）元素维护表单化**：若后续要降低 Excel 编辑门槛，可加一个只读→校验→写回的小工具（**注意**：本方案不含"自愈结果自动回写"，见 §1.2 非目标；此处仅指人工维护的辅助录入）。

**验收**
- 工作簿中不再存在 `查找元素：` 前缀的提示词。
- 体检脚本对全量 260 个元素的**错误级告警 = 0**；警告级告警逐条有结论（修正或标注接受）。
- 工作簿 `说明` sheet 含完整填写规范。
- `tests/` 全绿（`test_ui_element_runtime.py:37-57` 断言三列提示词映射，需同步更新夹具数据）。

**工作量**：3–4 人日（含业务描述撰写与评审；起草助手另计 1–2 人日）

---

### 阶段 2：元素模型元数据补齐（核心代码改动）

**改动**：`core/ui/element_runtime.py`

1. **三列提示词合并（本阶段最关键的一项）**：新增合并函数，把非空的
   `AI定位提示词1/2/3` 以 `\n` 连接，写入 **`elements[0].prompt`**；`elements[i>0].prompt` 置 `None`。
   - 依据 §3.4.1：文本 Agent 只读 `first_prompt()`，即 `elements` 中第一个非空 `prompt`。
   - 只填第 1 列时结果等于第 1 列，向后兼容。
2. 补齐其余字段：

| 字段 | 取值来源 | 说明 |
|---|---|---|
| `description_template` | 合并后的提示词 | **注意**：它**不进入**文本 Agent 的 `target.prompt`；作用是 `elements` 为空时的占位定位组合成、视觉兜底描述、变量追踪观测。设置它仍必要（阶段 3 的 AI-only 依赖它） |
| `element_version` | 定位器集合 **+ 合并后提示词** 的稳定哈希 | 提示词或定位表达式变更时自愈记录应失效；**不要用元素 `ID` 冒充** |
| `page_url` | 由 `页面名称` 映射到路由（**需一次映射表设计**，见 §未决问题 Q2） | 作为 `expected_page_url`，用于判断"是否找错页面" |
| `category` | 页面 key → **中文页面名** 映射（如 `componentsPage` → `组件演示页`） | 现状直接送页面 key（`prompt.py:33`），语义弱；映射后零成本提升 AI 上下文 |
| `collect_snapshot` | 按配置开关（默认 False） | 控制基线快照采集 |
| `name` 回退 | 若三列提示词全空，用 `说明` 列（过滤超长，如 >60 字则丢弃）作为描述回退 | `说明` 列 212/260 非空且当前只进 Allure 证据，属免费语义来源 |

3. `frame_path`：项目元素表**按 `AGENTS.md` 规定不允许写 iframe 运行行为**，因此本阶段**不填** `frame_path`，仅在文档中记录该限制对 iframe 元素自愈的影响。
4. 显式降级日志：`_configure_healing()` 对三种状态分别打日志（未启用 / 已启用 / Key 缺失），并把状态写入运行级产物。

**验收**
- 新增单测：三列非空 → `elements[0].prompt` 等于 `"\n".join(三列)`，且 `elements[1].prompt is None`；只填第 1 列 → 结果等于第 1 列；三列全空 → 用 `说明` 回退。
- 新增单测：`element_version` 在提示词变化后随之变化，在仅 `ID` 不变时保持稳定。
- 用 `harness.locate_sync()` 手调一次，确认 AI 请求体 `target.prompt` 确实是合并后的多行文本（可通过 fake model client 捕获请求断言）。
- 原有 324 条单测与全量 UI 回归全绿。

**工作量**：3–4 人日

---

### 阶段 3：AI-only（描述即定位）元素支持

**背景**：库支持"无固定定位器 + 有描述"的元素（`_sync_element.py:88-98` 合成 `is_placeholder=True` 占位定位组），但项目 `from_record()` 在无定位器时硬抛 `ValueError`。

**改动**
1. `ElementDefinition.from_record()`：当「无有效定位表达式」但「`AI定位提示词1` 非空」时，允许构造只含 prompt 的 `LocatorDefinition`（`method/expression` 留空，标记为描述型）。
2. `to_element_model()`：对描述型元素置 `elements[0].is_placeholder = True`、`exp=None`、`loc=''`。
3. 增加**前置校验**：描述型元素必须在 `AI_ELEMENT_HEALING_ENABLED=true` 且有 Key 时才允许执行，否则在收集期就报出清晰错误（而不是运行期失败）。
4. 文档补充：描述型元素的适用边界（仅用于稳定可见、语义明确的元素；不用于表格批量行内元素）。

**验收**
- 新增 1 个描述型元素（如 `ui-file-input` 的 AI-only 变体）并写一条能力用例，在关闭 AI 时**收集期**即报错、开启 AI 时能定位成功。
- 用 fake model client 做单元测试，不依赖真实 API（见 §6.1）。

**工作量**：2 人日

---

### 阶段 4：可观测性与门禁

**改动**
1. `core/ui/element_runtime.py`：从 `result.locator_engine` 提取 §3.5 字段，生成 Allure 步骤与附件（替代现在"埋在操作结果 JSON 里"的做法）。
2. 用例级标记：自愈成功的用例打 `healed` 标签（Allure label），便于筛选用例。
3. 运行级聚合：在 `core/execution/` 增加一轮运行的 AI 统计（调用次数 / 成功次数 / 熔断次数 / 按元素 Top N），写入运行产物。
4. markers 门禁：新增 `ai_heal` marker，配合库侧"无观察档"的现实，用**双跑对比**替代观察档（见 §6.2）。
5. 控制台：
   - 运行详情页展示 AI 统计；
   - 「元素自愈模式」下拉在库里失效（B4），要么移除、要么加提示说明，避免误导。
6. 修复 B3：把 `AI_*` 加入 `core/execution/catalog.py:101-104` 的 `.env` 白名单，使 `.env.*` 配置能在控制台预览。

**验收**
- Allure 报告中每条涉及自愈的用例都有独立「AI 自愈」步骤，字段完整。
- 一轮运行后能拿到 AI 统计产物。
- 控制台运行详情页能看到统计，且不再出现无法生效的「自愈模式」选项（或已标注说明）。

**工作量**：3–4 人日

---

### 阶段 5：测试、文档与常态化

**改动**
1. **fake model client 端到端测试**（关键）：构造一个返回固定 snapshot-ref 候选的假 `model_client`，注入 harness，验证「固定定位器失效 → AI 命中 → 操作成功 → `used_ai=true`」整条链路，**不调用真实 API**。
2. 真实 API 冒烟测试：`@pytest.mark.ai_smoke`，默认不执行，仅在显式提供 Key 的 CI job 中跑 1–2 个元素。
3. 文档：
   - 新增 `docs/guides/AI元素定位使用指南.md`：开关、参数含义、成本、观测、排障；
   - 在 `docs/guides/` 增加「提示词编写规范」（§3.4 内容）；
   - `AGENTS.md` 补一条：提示词只维护第 1 组、禁止模板串、Key 只走 Secret。
4. 清理 C5 死代码 `WebBaseObject`（若确认无引用）。

**验收**
- fake client 测试在无网络环境下通过。
- 文档评审通过，`AGENTS.md` 更新后与实现一致。

**工作量**：2–3 人日

---

## 5. 实施顺序与依赖

```text
阶段0 凭据与合规 ──┐
                   ├─→ 阶段1 提示词数据 ──→ 阶段2 元数据补齐 ──┐
（阻塞，可并行）    │                                          ├─→ 阶段4 观测与门禁 ─→ 阶段5 测试文档
                   └──────────────────────────────────────────┘
                                        阶段3 AI-only（可选，依赖阶段2）
```

- 阶段 0 与阶段 1 **可并行**（一个改代码、一个改数据）。
- 阶段 1 与阶段 2 的**合并在同一轮评审**：合并规则（§3.4.2）定下来，提示词才敢按三列结构填。
- 阶段 3 是可选增强，可延后。
- 总计约 **14–19 人日**（含可选的提示词起草助手 1–2 人日；不含提示词业务描述的评审往返时间）。

---

## 6. 验证方案

### 6.1 分层测试

| 层 | 手段 | 是否需真实 API |
|---|---|---|
| 单元 | fake model client 驱动 `locate_sync`；断言 metadata 各字段 | 否 |
| 集成 | 固定定位器故意写错 → 验证自愈接管并成功 | 否（用 fake client） |
| 真实冒烟 | 1–2 个元素走真实网关 | 是，独立 job |
| 回归 | 全量 6 项目 1839 条 | 取决于开关 |

### 6.2 双跑对比验收（核心手段）

因为库侧**没有"只建议不执行"的档位**（`mode` 硬编码为 2），无法先用观察档收集数据。因此采用双跑：

1. **基线跑**：`AI_ELEMENT_HEALING_ENABLED=false`，全量 6 项目，记录 pass/fail 集合。
2. **AI 跑**：`AI_ELEMENT_HEALING_ENABLED=true` + Key，同样全量。
3. **取差集**：
   - `基线失败 → AI 通过` = **AI 救回的用例**（收益）
   - `基线通过 → AI 失败` = **AI 引入的回归**（必须为 0，否则回滚）
4. **验收标准**：
   - 差值集合中"引入的回归" = 0；
   - "救回的用例" ≥ 预设目标（建议先以 `ui-file-input` 等已知问题元素为靶子）；
   - 记录 AI 调用次数与平均耗时，确认在预算内。

> 基线数据可复用本次升级验证已记录的结论：`1839 passed / 0 failed`。

### 6.3 回归门禁

- 默认 CI（无 Key）不开启 AI，保证 1839 条基线稳定。
- 独立的 `ai-heal` job 开启 AI，允许失败但不阻塞主流程（成熟后再纳入门禁）。

---

## 7. 风险与回滚

| 风险 | 影响 | 缓解 | 回滚 |
|---|---|---|---|
| AI 自愈掩盖真实回归（元素变了却被"猜"对） | 用例假绿 | 双跑对比；自愈用例打 `healed` 标签并单独复核 | 关 `AI_ELEMENT_HEALING_ENABLED` |
| 提示词质量不达标导致误定位 | 操作错元素 | 提示词体检告警；`AI_SEMANTIC_STRENGTH` 从 0 逐步提高 | 关开关 |
| 模型成本失控 | 费用 | 库内预算+熔断；项目侧调用次数告警；按 marker 收口 | 关开关 |
| 网关不稳定/鉴权失效 | 用例大面积超时 | 库内熔断（401 直接全局冷却）；`AI_TIMEOUT` ≤30s | 关开关 |
| Key 泄露 | 安全 | 阶段 0 全量整改；日志脱敏 | 轮换 Key |
| 库侧行为变更（如 `_heal_mode` 再次调整） | 方案失效 | 升级内部包时重跑 §6.2 | 固定内部包版本 |
| `page_url` 映射设计不当 | 自愈被错误页面约束 | 阶段 2 先小范围试；映射可配置 | 不填 `page_url` |

---

## 8. 需要 `mangoautomation` 配合的事项

建议作为需求提交给内部包：

1. **恢复 `mode` 语义**：`harness/web.py:86-90` 的 `_heal_mode()` 硬编码为 2，导致配置项被 advertise 却无效。建议恢复读 `runtime_config.locator_mode()`，使 mode 1（只建议）可作为真正的观察档——**这条能直接省掉双跑对比的复杂度**。
2. **`first_prompt` 支持多 slot 拼接**：目前只取第一个非空 prompt，元素表 3 组提示词列有 2 组浪费。
3. **非定位类异常不要进入自愈链路**：当前参数非法/文件缺失等操作级异常会被当作定位失败重试并自愈，最终用自愈文案覆盖真实异常（已在 `docs/guides/内部包升级记录.md` 记录实例）。
4. **开放运行时可调项**：`standalone()` 建议暴露 `fixed_retry_seconds` / `smart_timeout_seconds` / `visual_enabled`，目前被 `StaticRuntimeConfig` 写死。
5. **提示词 YAML 支持外部覆盖**：便于项目按被测产品定制规则。
6. **`memory_provider` / `event_sink` 默认持久化实现**：目前默认 `NullMemoryProvider` / `NullEventSink`，自愈记录用完即丢。
7. **澄清 `description_template` 与 `prompt` 的语义**：`description_template` **不进入**文本 Agent 的
   `target.prompt`（只用于占位定位组合成、视觉兜底、变量追踪），但命名容易被理解为"AI 描述模板"。建议在库文档中明确，或统一两者取值。
8. **`排除项` 解析应容错**：`positive_prompt()` 只做**行首**匹配，`排除项：` 若夹在描述句中会被当成
   **正向必需文本**，语义完全反转（已实测）。建议改为全文识别排除条件，或至少在解析到可疑写法时告警。
9. **`semantic_required_texts` 的整行回退值得商榷**：无引号、无分隔符的长句会被整体作为必需文本
   （实测 `在文件上传区域点击「选择文件」按钮` 整行进入必需列表），建议改为只取核心片段。

---

## 9. 未决问题（需评审决策）

| # | 问题 | 选项 | 建议 |
|---|---|---|---|
| Q1 | 控制台是否保留 `AI_API_KEY` 输入？ | ①保留但打码不落库 ②完全移除，只走 Secret | **②**：更简单且彻底合规；控制台仍可调模型/超时等非敏感项 |
| Q2 | `page_url`（期望页面）如何取值？ | ①元素表 `页面名称` 映射到路由 ②按 Page Object 声明 ③先不填 | **③ 先不填**，阶段 2 末尾再评估；避免过早引入映射维护成本 |
| Q3 | AI 定位的生效范围？ | ①全局 ②按 marker ③按运行参数 | **②+③**：默认关闭，显式开启 |
| Q4 | 是否引入视觉兜底？ | ①本期不做 ②二期评估 | **①**：需绕过 `standalone()` 并额外接多模态模型，成本与收益不明 |
| Q5 | 熔断隔离语义？ | ①整轮共享 ②每用例重置 | **①**：与库设计一致，避免重复烧钱 |
| Q6 | 是否要求自愈结果回写元素表？ | ①本期不做 ②做 | **①**：需要元素表写接口，属独立课题 |
| Q7 | **三列提示词是否合并为一处描述？** | ①合并进 `elements[0].prompt`（三列=三行结构）②只在第 1 列填，列 2/3 留空 ③等库侧改 `first_prompt` 支持多 slot | **①**：让三列全部生效且向后兼容；③ 周期不可控，可作为并行推动项 |
| Q8 | **`说明` 列是否作为描述回退？** | ①是（过滤 >60 字噪声）②否 | **①**：212/260 非空且是免费语义来源；但需先抽检内容质量 |
| Q9 | **提示词体检是告警还是阻断？** | ①错误级阻断、警告级告警 ②全部仅告警 | **①**：两个语义反转陷阱和未定义变量会造成静默错误结果，必须阻断 |
| Q10 | 是否开发提示词起草助手（纯规则、不调模型）？ | ①做 ②不做 | **① 建议做**：降低 260 条描述的撰写门槛，成本 1–2 人日 |

---

## 10. 附：元素读取链路与关键代码位置

### 10.1 元素读取链路（两条源，一个出口）

由项目设置 `ELEMENT_SOURCE` 选择数据源（`core/ui/config.py:15`，默认 `excel`）：

```text
ELEMENT_SOURCE = excel | feishu
  │
  ├─ excel  → core/sources/workbooks/mock_ui/mock_ui_elements.xlsx
  │           工作表「UI元素」；ExcelWorkbookSource.records()
  │           表头驱动 dict(zip(headers, values))，只强校验 7 个必填列
  │
  └─ feishu → DocumentData().ui_element()，按「项目名称」过滤
  │           （16 列旧表 → 补列重排为 18 列，document_data.py:128-131）
  │
  ▼ load_ui_element_records()          core/sources/ui_elements.py:27   (lru_cache maxsize=12)
  ▼ _validate_element_records()        :65   非空 / 产品名匹配 / 元素名唯一 / ID 唯一
  │
  ▼ ElementDefinition.from_record()    core/ui/element_runtime.py:124   18 列 → dataclass
  ▼ SourceElementRepository            core/ui/element_repository.py:16
  │      └─ 按 模块名称 / 页面名称 范围过滤；同名元素报错要求限定范围
  ▼ configured_element_repository(settings)
  ▼ ElementRuntime.execute() → to_element_model() → ElementModel → mangoautomation
```

**要点**：
- `PRODUCT_WORKBOOKS`（`ui_elements.py:21-23`）只注册 `mock_ui` 一个产品，三个 UI 项目**共用同一个 260 行工作簿**，符合 `AGENTS.md`「同一被测产品禁止按测试模式复制数据」。
- 读取层是**表头驱动、宽松**的：`ExcelWorkbookSource` 只校验 `REQUIRED_ELEMENT_HEADERS`（7 列），多列少列都不报错。但规范层有 3 道闸门——`AGENTS.md:113-115`、`CANONICAL_ELEMENT_HEADERS`、`tests/test_ui_element_runtime.py:118-130` 的硬断言。
- 因此**新增列必须走规范变更流程**，见 §3.4 ①。
- 现状数据特征（实测）：260 行全部 `定位方式1 = TEST_ID`、无一行缺 `定位表达式1`（即当前**没有** AI-only 元素）；`模块名称` 与 `页面名称` 260 行取值完全相同，`模块名称` 暂无额外区分度（既有结构，不建议改动）。

### 10.2 关键代码位置索引

| 主题 | 位置 |
|---|---|
| 元素读取入口（Excel/飞书分流） | `core/sources/ui_elements.py:27` |
| 元素表 18 列规范 / 必填列 | `core/sources/element_schema.py:3-32` |
| Excel 只读源（表头驱动） | `core/sources/excel.py:20-46` |
| 飞书 16→18 列映射 | `core/sources/feishu/document_data.py:74-131` |
| 元素仓库（范围过滤/同名检测） | `core/ui/element_repository.py:16-90` |
| 18 列 → dataclass | `core/ui/element_runtime.py:124-160` |
| 元素工作簿 | `core/sources/workbooks/mock_ui/mock_ui_elements.xlsx` |
| AI 配置常量 | `core/settings/settings.py:25-32` |
| AI 配置字段（可被 env 覆盖） | `core/ui/config.py:28-55` |
| 引擎装配 | `core/ui/element_runtime.py:197-213` |
| 提示词读取 | `core/ui/element_runtime.py:144-147` |
| 模型构造 | `core/ui/element_runtime.py:162-180` |
| 证据附件 | `core/ui/element_runtime.py:272-299, 328-346` |
| 控制台运行参数注册 | `auto_tests/project_registry.py:27-46` |
| 运行参数校验/白名单 | `core/execution/catalog.py:55-104` |
| 运行参数注入子进程 | `core/execution/command_builder.py:56` |
| 运行参数落库 | `web_console/run_service.py:56-71` |
| 现有 AI 相关测试 | `tests/test_ui_element_runtime.py:133-191, 261-276` |
| 既有自愈问题记录 | `docs/guides/内部包升级记录.md` |
| **提示词 → AI 描述的取用点** | 库 `element_healing/context/sanitizer.py:7-12`（`first_prompt`） |
| **AI 请求体里的 `target.prompt`** | 库 `element_healing/agent/web/prompt.py:34` |
| 提示词按行解析 / 排除项剔除 | 库 `element_healing/context/sanitizer.py:15-21`（`positive_prompt`） |
| 必需文本派生（引号 / 「的」后缀） | 库 `element_healing/context/sanitizer.py:57-83` |
| 提示词 `${{变量}}` 替换 | 库 `uidrives/_sync_element.py:349-351` |
| 描述型元素占位定位组合成 | 库 `uidrives/_sync_element.py:88-98` |
| 控件种类/作用域关键词表 | 库 `element_healing/verification/target_intent.py:43-87` |
| 提示词填写规范落点 | 元素工作簿 `说明` sheet |

---

## 11. 实施结果与偏差（2026-09-30）

阶段 0–5 已全部实施。以下记录落地物、与原方案的偏差及原因、以及仍未完成的事项。

### 11.1 落地物

| 阶段 | 落地物 |
|---|---|
| 0 合规 | `core/execution/secrets.py`（敏感字段识别/脱敏/清理）；控制台移除 `AI_API_KEY` 与失效的 `ELEMENT_HEALING_MODE`；`app.py` 对外边界脱敏；`catalog._safe_env_values` 放行 `AI_*` 并脱敏；`repository` 启动清理历史明文；`app.js` 补 `password` 渲染分支 |
| 1 数据 | `core/sources/prompt_spec.py`（三列合并 + 体检）；`main.py --check-elements`；260 行提示词按三列结构回填；工作簿 `说明` sheet 追加填写规范；飞书源去掉模板串兜底 |
| 2 元数据 | `core/sources/page_labels.py`；`element_runtime` 合并提示词写入 `elements[0].prompt`、补 `description_template` / `element_version`（定位器+提示词哈希）/ 中文 `category` / `说明` 列回退 / 显式降级日志 |
| 3 描述型元素 | `from_record` 支持无定位器但有提示词；`to_element_model` 交给库合成占位定位组；构造期与执行期双重前置校验；删除 3 个死属性 |
| 4 可观测性 | `core/ui/healing_metrics.py`（运行级统计 + 多 worker 合并）；「AI 自愈」Allure 附件与 `healed`/`heal_source`/`heal_mode`/`heal_model` 标签；`pytest_sessionfinish` 落盘与终端摘要；控制台 `GET /api/runs/{id}/ai-healing` + 运行详情页面板；三个 UI 项目声明并自动标注 `ai_heal` marker |
| 5 测试文档 | `tests/test_ai_element_locating.py`（fake model client 端到端，`-m ai_e2e`）；`tests/test_ai_element_locating_smoke.py`（真实网关冒烟，默认跳过）；`AI元素定位使用指南.md`；`AI定位提示词编写规范.md`；`AGENTS.md` 与 `README.md` 更新 |

### 11.2 与原方案的偏差

| 项 | 原方案 | 实际处理 | 原因 |
|---|---|---|---|
| `collect_snapshot` | 按配置开关接线 | **未接线** | 实测：冻结的快照写入 `ElementResultModel._baseline_snapshot`，但该字段在包内**只有写入没有读取**，且默认 `NullMemoryProvider` 不持久化。接线等于新增死配置，改为列入上游需求 |
| `page_url` | 由 `页面名称` 映射到路由 | **未填** | 依 Q2 决定：站点为 hash 路由、URL 随环境变化，映射维护成本高于当前收益；先用中文 `category` 提升上下文 |
| `WebBaseObject` | 确认无引用后删除 | **保留** | 它是 `core.ui` 的**导出面**（`core/ui/__init__.py` 对外导出），删除公共 API 应由维护者确认是否被下游复用；此处只记录，不静默删除 |
| `ELEMENT_HEALING_MODE` | 保留并加提示说明 | **从控制台移除** | 库侧硬编码为 2，1/2/3 无任何行为差异；保留一个不生效的下拉框只会误导。设置常量保留并加注释，待上游恢复语义后重新暴露 |
| 提示词起草助手 | 独立工具 | **一次性迁移脚本** | 生成逻辑依赖本产品元素的名称/说明语料，做成通用工具价值有限；数据已回填，后续按需重跑 |
| 提示词内容 | 业务描述撰写（2–3 人日评审） | **结构化草稿** | 260 条描述由「元素名 + 说明 + 页面」规则生成，已通过体检（0 错误 0 警告），但**仍需业务评审润色**；见 §11.4 |

### 11.3 验证结果

| 范围 | 结果 |
|---|---|
| `tests/` 单测（含 5 条 AI 端到端） | **370 passed** |
| 提示词体检（全量 260 元素） | 错误 0 · 警告 0（改造前：警告 780） |
| `-m ai_heal` 定向选择 | 三个 UI 项目各精确选中 5 条 |
| AI 链路端到端（fake model client） | 模型调用 1 次即命中 `get_by_role('button', name='确认提交')`，`used_ai=true`，`decision=temporary_heal` |
| 本地确定性候选 | 描述含可见文案时**调用模型 0 次**（费用保护生效） |
| 合规 | 控制台与 API 均不再暴露/回显凭据；历史明文在仓库初始化时清除；数据库保留原值供执行使用 |

### 11.4 仍未完成 / 需人工介入

1. **提示词业务评审**：260 条描述是结构化草稿。体检只能保证"结构正确、无反转陷阱"，**不能保证语义准确**，需业务方按《AI 定位提示词编写规范》逐条确认。
2. **真实网关验证**：本机无任何可用凭据（环境变量与 `.env.*` 均为空），因此未执行真实模型调用；`tests/test_ai_element_locating_smoke.py` 已就绪，注入 `AI_API_KEY` 即可验证。
3. **双跑对比**：需在有凭据的环境执行 §6.2 的对比实验，才能得出"AI 救回了哪些用例"的结论。
4. **上游需求 9 条**（§8）尚未提交给 `mangoautomation`，其中"恢复 `mode` 语义"能直接简化双跑流程。
5. `WebBaseObject` 的去留待维护者确认。
