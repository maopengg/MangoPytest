# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

芒果测试平台 (mango_pytest) — 集 API/UI 自动化测试于一体的测试平台。

## 内部包使用规范（必须遵守）

本项目与 `/Users/mango/code/qfei-auto-platform` 使用同一套芒果内部包：

| 源码仓库 | Python 包 | 本项目联调版本 |
|---|---|---|
| `/Users/mango/code/mango_tools` | `mangotools` | `2.0.8` |
| `/Users/mango/code/mango_automation` | `mangoautomation` | `2.1.0` |

- `mangotools` 和 `mangoautomation` 禁止从 PyPI 安装；PyPI 版本是旧实现。
- 第三方依赖、gRPC 生成工具和内部包统一维护在 `requirements.txt`；
  内部包使用本项目 `local_packages/` 中与 `qfei-auto-platform` 一致的 wheel，
  禁止改为 PyPI 包名安装，内部包关联提供的三方依赖不重复声明。
- 只查看内部包源码时无需同步。若修改了内部包源码，必须先在对应源码仓库运行
  `sync_local_package.py`，再将生成的 wheel 同步到本项目 `local_packages/` 并更新版本声明。
- `mangotools` 按职责从具体模块导入，例如 `data_processor`、`decorator`、
  `models`、`exceptions`、`enums`；禁止依赖未声明的兼容导出。
- `mangoautomation` 统一从 `mangoautomation.uidrives`（复数）导入；禁止使用
  已移除的 `mangoautomation.uidrive`。
- Web 生命周期由 `WebDriverFactory` 创建的 `SyncWebRuntime` / `AsyncWebRuntime`
  管理；`BaseData` 通过 `bind_web(runtime, context, page)` 绑定上下文。
- 新代码禁止使用旧的 `DriverObject` 聚合器。pytest 同步 UI 用例使用
  `SyncWebRuntime`，异步执行器才使用 `AsyncWebRuntime` 与 `AsyncElement`。
- 包异常分别捕获 `mangoautomation.exceptions.MangoAutomationError` 和
  `mangotools.exceptions.MangoToolsError`，不要用宽泛异常替代可识别的业务异常。

## Architecture（必须遵守）

API/UI Demo 按项目定位使用不同的五层架构，禁止把不同模式混用：

### 轻量 API 项目（`simple_api`）

```text
Tests → Fixture → Factory + Repository → 公共 HTTP 客户端
```

- `simple_api` 禁止新增 Feature、Steps 或 `pytest_bdd` 依赖。
- 它只演示少量基础 HTTP Case，不承担大型项目业务编排。

### BDD 项目（`bdd_api`）

```
L5: Feature 文件（Gherkin 中文语法）
    ↓
L4: Steps 步骤定义层（common/api/auth/data/assertions）
    ↓
L3: Data Factory（entities/factories/specs）
    ↓
L2: Repositories（按业务域分包，自动清理）
    ↓
L1: 公共协议客户端 / 数据库 Gateway
```

### 纯 pytest 项目（`pytest_api`）

```
L5: Tests（pytest 测试、marks、参数化与断言）
    ↓
L4: Services / Workflows（业务场景与跨协议编排）
    ↓
L3: Data Factory（entities/factories/specs）
    ↓
L2: Repositories（按业务域分包，自动清理）
    ↓
L1: 公共协议客户端 / 数据库 Gateway
```

- `pytest_api` 禁止新增 Feature、Steps 或 `pytest_bdd` 依赖。
- Tests 和 Steps 均禁止直接访问协议客户端私有字段。
- HTTP、WebSocket、SSE、MCP、gRPC 统一复用 `auto_tests/common/mango_mock/`。

### BDD UI 项目（`bdd_ui`）

```
L5: Feature 文件（中文业务 Gherkin）
    ↓
L4: Steps（领域步骤、公共步骤、断言步骤）
    ↓
L3: 被测产品公共 Flows + 项目 Data Factory（entities/factories/specs）
    ↓
L2: 被测产品公共 Page Objects + Repositories + 本地 Excel 元素仓库
    ↓
L1: SyncWebRuntime / 公共协议客户端 / 数据库 Gateway
```

### 纯 pytest UI 项目（`pytest_ui`）

```
L5: Tests（pytest 测试、marks、参数化与业务断言）
    ↓
L4: 被测产品公共 Flows（跨页面业务场景编排）
    ↓
L3: Data Factory（entities/factories/specs/scenarios）
    ↓
L2: 被测产品公共 Page Objects + Repositories + 本地 Excel 元素仓库
    ↓
L1: SyncWebRuntime / 公共协议客户端 / 数据库 Gateway
```

- `pytest_ui` 禁止新增 Feature、Steps 或 `pytest_bdd` 依赖。
- `bdd_ui` 的业务 Feature 禁止使用“执行 UI-xxx 用例”式编号转发步骤；
  框架操作能力矩阵必须放在独立的 `features/capabilities/` 下。
- UI 元素读取统一由 `core/sources/` 管理；项目设置使用
  `ELEMENT_SOURCE=excel|feishu` 选择来源。
- UI 元素表固定为 18 列：`ID`、项目/模块/页面/元素名称，以及 3 组
  `定位方式`、`定位表达式`、`元素下标`、`AI定位提示词`，最后为`说明`；
  iframe、等待、快照、交互状态等运行行为禁止写入元素表。
- 3 组 `AI定位提示词` 是**同一段描述的三行**，运行时按行合并后写入
  `ElementModel.elements[0].prompt`（库侧只读第一个非空 prompt）。列语义固定为：
  列 1 控件描述（必填）、列 2 所在区域（可选）、列 3 排除项（可选，必须
  `排除项：` 独占行首）。多行必须用换行，禁止用 `|` 等分隔符拼接。
- 元素定义允许「只有 AI 定位提示词、不填定位方式/表达式」的描述型元素；这类元素
  必须开启元素自愈才能执行，未开启时在 `ElementRuntime` 构造期直接报错。
- 提交元素表改动前必须执行 `python main.py --check-elements`，错误级结论为 0。
  编写规范见 `docs/guides/AI定位提示词编写规范.md`。
- 元素自愈和 AI 的开关、模式、模型、服务地址、超时及语义强度统一在
  `core/settings/settings.py` 设置，并允许项目运行参数覆盖；真实 API Key 禁止入库，
  也禁止在控制台录入：只允许通过环境变量或 CI Secret 注入（`AI_API_KEY`）。
- AI 元素定位**默认关闭**；定向验证用 `-m ai_heal` 只跑元素自愈靶场用例，
  不要为验证 AI 而全量开启（库侧没有"只建议不执行"的模式）。使用方式见
  `docs/guides/AI元素定位使用指南.md`。
- 本地元素 Excel 统一存放在 `core/sources/workbooks/` 并按被测产品命名；
  测试同一产品的不同 Demo 必须复用同一元素工作簿，禁止按测试模式复制数据。
- 同一被测产品的 Page Object、Flow、Repository、能力执行器和能力用例模型统一
  放在 `auto_tests/common/<product>/`；BDD/pytest 项目只保留各自的用例表达、
  Fixture 装配、数据工厂和项目配置，禁止复制产品业务实现。
- UI 项目统一复用 `core/ui/` 的元素仓库、Runtime 参数、浏览器生命周期、
  临时设备切换以及截图/HTML/控制台日志/Trace 产物能力；项目 Fixture 只负责
  Case 判定和注入本项目的业务对象，禁止复制公共浏览器基础设施。
- Tests、Steps 和 Flows 禁止直接操作 Playwright Locator；页面行为必须进入 Page Object。
- Page Object 禁止创建测试数据或编写 pytest 业务断言。

## 测试用例编写规范

### 0. 全局 Case 分类与命名规范（强制）

- 所有 API/UI、BDD/纯 pytest 项目统一使用“自动化项目 → Epic（被测产品）→
  Feature（一级模块）→ Story（可选子模块）→ Case”的报告层级。
- Web Console 从项目注册表提供“自动化项目”；每条非架构 Case 必须显式提供
  Epic、Feature、稳定 Case ID 和中文业务标题，禁止显示原始 `test_xxx[...]`。
- Case 标题统一为 `<CASE-ID> <中文业务名称>`；参数化 ID 仅用于 pytest 节点，
  不能代替 Allure 标题。
- 一个测试文件只表达一个一级模块；业务域、能力类型不同必须拆分文件。
  参数数据可以集中维护，但测试表达层禁止把操作、交互、元素清单和业务流程混在同一文件。
- 参数化 Case 必须调用 `core.execution.apply_case_metadata`；禁止各项目自行拼接
  不一致的 Epic/Feature/Story/Title。
- BDD 项目以 Feature 名作为 Feature 分类、Scenario 名作为 Case 标题；绑定文件必须
  与单个 Feature 一一对应，禁止一个 `scenario(...)` / `scenarios(...)` 绑定多个业务模块。

### 1. BDD Feature 文件规范

- 使用中文 Gherkin 语法（`# language: zh-CN`）
- 每个场景对应一个接口测试
- 断言至少包含状态码和业务 code

```gherkin
# language: zh-CN
功能: 模块名称
  场景: 获取XX信息
    当 用户获取XX信息
    那么 响应状态码为 200
    并且 code 为 200
    并且 success 为 true
```

### 2. BDD 步骤定义规范

- 使用 `target_fixture="api_response"` 传递响应数据
- 返回 `{"response": response, "status_code": ..., "data": ...}` 格式
- 使用 `core.utils.log` 记录日志

### 3. 数据创建规范

- 使用 Factory 创建测试数据：`假如 存在"用户"`
- 测试数据以 `AUTO_` 开头，便于自动清理
- **禁止**在测试用例中直接调用 API 创建数据

### 4. 纯 pytest 用例规范

- 测试函数只调用 Factory、Repository 或 Service 的公开方法。
- 每条用例保留 Case ID，并使用 pytest mark / Allure 元数据关联。
- 请求和响应优先使用 Pydantic 强类型模型；边界场景使用参数化。
- 前置数据通过 fixture + Factory 创建，清理由 fixture + Repository 完成。
- 禁止使用按 Case ID 编号区间路由的集中执行器。

### 5. 日志使用规范

- ✅ **优先使用 `debug`** — 大部分日志应该是 debug 级别
- ✅ 循环内部、频繁调用的方法必须使用 `debug`
- ✅ 关键业务节点（开始/结束/结果）使用 `info`
- ✅ 异常处理中使用 `error` 或 `warning`

## Running Tests

**必须使用 `.venv` 虚拟环境 + 设置 `ENV` 环境变量：**

```bash
# 安装公共依赖和与 qfei-auto-platform 一致的本地内部包
.venv/bin/python -m pip install -r requirements.txt

# 通过 main.py 执行完整测试
ENV=test .venv/bin/python main.py

# 生成 Allure 报告
allure generate ./runtime/reports/allure-results -o ./runtime/reports/allure-html --clean
```

## 文件与目录放置规范（强制）

新增或迁移文件前，先判断它验证或服务的是公共框架还是某个产品，再按下表选择目录。文件名带 `test_`、使用 pytest 或不连接真实环境，都不能作为放入根 `tests/` 的依据。不要在仓库根目录或公共目录新建业务脚本、业务模型和临时输出。

| 文件职责 | 应放位置 | 边界 |
|---|---|---|
| 仓库入口与说明 | 根 `main.py`、`README.md`、`AGENTS.md` | 入口只做调度；README 说明使用方式；AGENTS 规定维护边界，不堆放业务实现 |
| 依赖、测试默认策略与忽略规则 | 根 `requirements.txt`、`pytest.ini`、`.gitignore` | 依赖只维护一个入口，内部包使用本地 wheel；项目专属 pytest 策略留在项目目录 |
| 项目及可执行环境登记 | `auto_tests/project_registry.py` | 新项目、默认项目 `DEFAULT_PROJECT` 和环境显式注册，不在公共入口、控制台或临时脚本中写死业务项目 |
| API/UI 业务回归表达 | `auto_tests/api/<project>/test_cases/`、`auto_tests/ui/<project>/test_cases/` | 断言真实产品规则、权限、状态或数据一致性的用例，不得放根 `tests/` |
| BDD Feature 与步骤 | 对应项目的 `features/`、`steps/` | 仅 BDD 项目使用；纯 pytest 和轻量 API 项目不引入这两层 |
| API 场景服务和编排 | 对应项目的 `services/` 或已约定的 `workflows/` | 不放根 `core/`、`web_console/` 或测试文件中；纯 pytest 遵守既定五层架构 |
| 业务实体、数据构造、场景规格 | 对应项目的 `data_factory/{entities,factories,specs}/` | 公共 Factory 基类才进入 `core/base/`，业务字段和业务样本不进入公共基类 |
| 业务数据访问与清理 | 对应项目的 `repositories/`，BDD 项目按已有约定放 `repos/` | 数据访问及清理由 Repository 负责，不写进 Tests、Steps 或 Page Object |
| 同一产品复用的协议实现、Page Object、Flow、Repository | `auto_tests/common/<product>/` | 只在该产品内共享，不能因多个业务项目都用到就提升为公共框架 |
| 具体项目或产品的离线检查、迁移检查、适配验证 | `auto_tests/<kind>/<project>/tests/` 或 `auto_tests/common/<product>/tests/` | 必须通过显式路径执行；不与业务回归 `test_cases/` 混放，也不回流根 `tests/` |
| 业务配置与 Fixture 装配 | 对应项目的 `config/`、`fixtures/`、`conftest.py` | 公共生命周期复用 `core/`，项目只负责本项目判定、对象组装和参数注入 |
| 非敏感业务样例、上传模板、维护数据 | 对应项目的 `data/` 或既有资产目录 | 维护资产不放 `runtime/`；真实凭据和运行生成的登录态不作为业务样例提交 |
| 产品 UI 元素工作簿 | `core/sources/workbooks/<product>/` | 属于按产品管理的数据资产，不代表该产品测试可以放入根 `tests/`；同一产品复用一份工作簿 |
| 通用 HTTP、DAL、执行、UI 生命周期和数据源能力 | `core/api/`、`core/dal/`、`core/execution/`、`core/ui/`、`core/sources/` | 必须独立于具体产品、Case ID、环境地址和业务配置，不放项目专属分支 |
| 公共基类、配置、模型和枚举 | `core/base/`、`core/settings/`、`core/models/`、`core/enums/` | 只承载框架契约和默认参数，不承载业务域模型或真实凭据 |
| 公共框架自身的验证 | 根 `tests/`，按下节分类 | 使用可独立构造的样例；不得为同步公司与开源框架增加业务适配版测试 |
| 控制台接口、页面与静态资源 | `web_console/`，按其 README 的分层 | 控制台只负责公共管理与展示，不嵌入某个产品的业务客户端和用例逻辑 |
| 可选公共 HTTP 模拟服务 | 根 `mock/` | 两边保持相同实现；仅显式启动，不嵌入真实业务凭据；产品专属模拟放 `auto_tests/common/<product>/mock/` |
| 仓库级维护脚本 | 根 `scripts/` | 仅放框架维护、迁移和通用检查；依赖产品身份、接口或配置的脚本放对应项目的 `scripts/` |
| 操作指南、架构说明、设计方案与文档图片 | `docs/guides/`、`docs/architecture/`、`docs/plans/`、`docs/assets/` | 各目录 README 放本目录职责、入口和维护方式；历史材料放 `docs/archive/`，不当作当前执行指引 |
| 内部包 wheel 与构建来源记录 | `local_packages/` | 版本声明维护在根 `requirements.txt`，源码与 SHA256 记录在构建清单，不把内部包源码复制进公共模块 |
| 日志、报告、缓存、下载和临时执行数据 | `runtime/` 的对应子目录 | 统一通过 `core.runtime` / `artifact_path` 解析，不新增顶层 `artifacts/`、`logs/`、`report/`，不提交运行产物 |
| 本地敏感运行配置与生成的登录态 | `runtime/config/<project>/`，或项目已有且被忽略的私有路径 | API Key 使用环境变量或 CI Secret；凭据文件不提交；已有约定路径的迁移单独核对引用，不能只改文档就搬文件 |
| 编辑器运行与检查配置 | `.vscode/` 等既有工具目录 | 只放工具配置，不承载测试数据、业务配置或执行结果 |

- “公共”表示不依赖任何具体产品的业务语义；多个产品碰巧复用同一段业务实现，不足以将它放进 `core/` 或根 `tests/`。
- 修改已有实现前先沿用对应目录的职责；拆分文件按实际能力命名，不新增泛化的 `misc/`、`temp/` 或根级杂物文件来绕过分类。
- 新增 Python 包目录补齐 `__init__.py`；迁移时同步修改导入、动态插件路径、模板、静态资源、文档和测试，不保留旧路径转发空壳。
- 本表规定后续新增与迁移的归属，不自动授权启动服务、执行真实业务或搬迁历史凭据；这些操作仍遵守当前任务授权和项目运行约束。

## 公司与开源同步边界（强制）

- 除具体业务外，所有维护文件按开源基准对齐，包括 `main.py`、`core/` 公共代码、`tests/`、`web_console/`、`mock/`、公共 `scripts/`、依赖、工具配置、公共文档和本规范。
- 允许不同的范围仅为：`auto_tests/` 中的项目与注册表、`core/sources/workbooks/` 产品元素资产、`docs/assets/test-cases/` 产品用例表，以及说明各自仓库身份与业务用法的根 `README.md`。
- 公司业务规范写在 `auto_tests/AGENTS.md`，业务脚本和设计资料归对应业务项目；禁止通过保留根级业务目录或给公共框架加公司分支来规避对齐。
- 用 `.venv/bin/python scripts/check_framework_alignment.py --upstream <另一仓库路径>` 检查。该命令比对 Git 跟踪文件及未忽略的新文件，按字节校验；本地虚拟环境、编辑器私有状态和 `runtime/` 不属于同步内容。不得为了通过检查随意扩大业务排除范围。

## 公共框架测试目录（强制）

根 `tests/` 的唯一职责是证明公共框架能力正常，开源与公司仓库的这棵目录及内容应保持一致。它不是所有 pytest 文件的收纳目录，也不是业务回归的备用入口。

允许验证的内容与放置位置：

| 子目录 | 验证对象 |
|---|---|
| `architecture/` | 通用 Case 元数据和框架分层边界，不检查某个业务项目的具体文件数或场景清单 |
| `runtime/` | 运行目录、输出配置、日志及历史产物迁移 |
| `execution/` | 通用命令构建、项目发现、环境解析、结果解析、证据与脱敏 |
| `data/` | 公共 Factory、Repository 基类和数据血缘，使用临时实体与内存数据库 |
| `dal/` | 通用表达式、路径、运算符、Schema 及中文断言步骤；按 unit/integration/features 分类 |
| `ui/` | 通用元素源、模型装配、提示词、自愈统计和浏览器生命周期；工作簿与产品映射由临时 Fixture 构造 |
| `web_console/` | 通用控制台接口、收集、执行、报告和存储；使用模拟注册表及临时项目 |
| `integration/ui/` | 需要真实浏览器或 AI 网关的公共框架验证，使用 `browser_e2e`、`ai_e2e`、`ai_smoke` 标记 |

以下内容禁止放入根 `tests/`：

- 具体产品的接口、UI、权限、租户隔离、合同、订单、字段同步等业务回归。
- 业务代码的离线单元测试、模拟响应测试、业务 Workflow/Factory 测试、具体项目迁移门禁；即使不联网，它们仍属于业务项目。
- 依赖某个产品真实工作簿、Case ID 清单、场景数量、项目配置类、账号或维护样本的检查。
- 为公司仓库编写的合同适配版本，或为开源仓库编写的 Demo 适配版本。项目特有内容留在对应 `auto_tests/` 范围，不能让公共套件因仓库不同而改写。

公共测试不直接导入 `auto_tests` 下的业务项目，不读取其私有配置或维护资产。项目注册表、工作簿、文件、响应和数据库使用临时样例及 Fixture；无法脱离具体产品构造前置时，应判定为项目专属测试。

离线框架回归：

```bash
ENV=test .venv/bin/python -m pytest tests -m 'not ai_e2e and not ai_smoke and not browser_e2e' -q
```

框架分层门禁在 `tests/architecture/test_layer_boundaries.py` 中检查业务导入和控制台依赖边界，不得通过关闭门禁、增加忽略项或引入旧路径转发来规避。分类和执行说明见 `tests/README.md`。

## Web Console 目录

- `web_console/app.py` 只装配应用、生命周期和服务；HTTP 路由与依赖放 `api/`，请求模型放 `schemas/`，调度与报告逻辑放 `services/`，持久化放 `repositories/`，pytest 收集插件放 `plugins/`。
- 页面模板放 `templates/pages/`；静态资源由 `static/js/app.js` 和 `static/css/app.css` 入口加载。JS 按 `common/pages/reports` 拆分并显式导入，只将模板事件处理函数注册到 `window`。
- 路由不直接访问 SQLite、运行子进程或拼接产物路径；Service 不依赖 FastAPI。目录、调用关系和验证命令见 `web_console/README.md`。

## Available Fixtures

| Fixture | Purpose |
|---------|---------|
| `api_response` | 步骤间传递响应的 fixture |

## Available Assertion Steps

**强制使用 DAL 断言（`core/dal/bdd_steps.py`）**：

| Gherkin 步骤 | 说明 |
|---|---|
| `响应状态码应该为 {code}` | 验证 HTTP 状态码 |
| `响应字段 "{field}" 应该为 "{value}"` | 验证响应 JSON 字段 |
| `响应数据 "{field}" 应该为 "{value}"` | 验证 data 内业务数据 |
| `响应数据应该包含字段 "{field}"` | 验证字段存在性 |
| `响应数据应该是列表` | 验证数据类型 |
| `列表长度应该为 {length}` | 验证列表长度 |
| `响应消息应该包含 "{text}"` | 验证消息内容 |

**DAL 表达式断言（推荐）**：
```gherkin
那么 响应应该为:
  """
  status_code = 200
  body.code = 200
  body.data.size > 0
  """
```

## Required Test Marks (from pytest.ini)

每个测试文件应添加 `pytestmark`，包含合适的标签。已有标签：
`smoke`, `positive`, `negative`, `security`, `integration`, `auth` 等。

## 禁止

- ❌ 在测试用例中直接调用 API 创建数据
- ❌ 在测试用例中写数据清理逻辑
- ❌ 在测试用例中定义配置常量
- ❌ 不遵守五层架构


## 本地运行产物

- 所有运行产物通过 `core.runtime.runtime_root/runtime_path` 或 `artifact_path` 解析，默认写入 `runtime/`；禁止新建顶层 `artifacts/`、`logs/`、`report/` 等并行输出目录。
- 日志固定为 `runtime/logs/` 下的五级 `*-log.log` 文件；控制台状态与收集缓存位于 `runtime/cache/web_console/`。
- `MANGO_PYTEST_RUNTIME_DIR` 可覆盖运行根目录。测试数据、元素工作簿、模板属于维护资产，不放进运行目录。
