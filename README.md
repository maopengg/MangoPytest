# MangoPytest · API / UI 自动化示例项目

一个面向真实项目结构设计的开源 pytest 自动化测试示例仓库，统一演示 API、UI、BDD、数据工厂、多协议测试、Allure 结果采集和本地 Web 测试控制台。

项目不是把所有用例堆在同一种目录中，而是为团队提供三种可独立选择的自动化方式：轻量 Demo、BDD 和纯 pytest 大项目架构。仓库包含 7 个自动化项目，其中 6 个 API/UI Demo 已启用，SQL 项目作为数据库专项自动化的扩展位置。API 与 UI 项目共享框架基础能力，但各自保留独立的业务用例、数据工厂和配置，便于学习、对比和直接用于新项目脚手架。


[Gitee 仓库](https://gitee.com/mao-peng/mango_pytest) · [GitHub 仓库](https://github.com/maopengg/MangoPytest) · [在线帮助文档](http://160.202.231.91:36696/pages/mango-pytest/deploy.html) · [芒果测试平台 Demo](http://160.202.231.91:35966/#/index/home) · [Mango Mock 靶场](http://160.202.231.91:20017)

## 从这里开始

| 你的目标 | 对应入口 |
| --- | --- |
| 安装并跑通第一个 Demo | [启动与运行 Demo](http://160.202.231.91:36696/pages/mango-pytest/deploy.html) |
| 从网页选择、执行用例并查看结果 | [Web 控制执行](http://160.202.231.91:36696/pages/mango-pytest/Web控制台.html) |
| 新增自己的项目、修改设置、了解数据存储位置 | [项目与配置](http://160.202.231.91:36696/pages/mango-pytest/项目与配置.html) |
| 了解六种 API/UI Demo 的功能 | [Demo 功能说明](http://160.202.231.91:36696/pages/mango-pytest/function_Introduction.html) |

可以独立在本机运行，不要求先部署芒果测试平台。用例采用普通 pytest、BDD 或其他组织方式，由你根据业务需要选择；仓库中的 Demo 用于对比和参考，不要求所有项目都照搬同一套分层。

## 主要能力

- 多项目管理：通过统一注册表收集并运行 API、UI 和其他类型的自动化项目。
- 三种开发模式：轻量 pytest、中文 Gherkin BDD、适合大型项目的分层纯 pytest。
- 多协议 API：除标准 HTTP 外，还覆盖 WebSocket、SSE、gRPC、MCP、Webhook 等测试方式。
- UI 自动化：基于 Playwright 与 `mangoautomation`，支持 Page Object、结构化操作步骤、元素模型和元素自愈。
- 测试数据：使用 Factory、Repository 和测试运行隔离管理数据，并在结果中展示数据血缘。
- 结构化结果：采集 Case、测试数据、请求、响应、UI 操作、日志、截图、Fixture 和 Allure 附件。
- Web Console：浏览本地项目文件和源码，执行项目、文件或单条用例，查看实时日志与历史结果。
- 本地内部包：`mangotools`、`mangoautomation` 使用仓库内 wheel，不依赖 PyPI 上的旧版本。

## 7 个自动化项目

| 类型 | 项目 | 分层方式 | 适用场景 |
|---|---|---|---|
| API | `simple_api` | Tests → Fixture → Factory/Repository → HTTP | 入门、小型项目、少量基础接口 |
| API | `bdd_api` | Feature → Steps → Factory → Repositories → 公共协议 | 业务评审、验收测试、多人协作 |
| API | `pytest_api` | Tests → Services/Workflows → Factory → Repositories → 公共协议 | 大型项目、多业务域、多协议编排 |
| UI | `simple_ui` | 数据驱动的轻量 UI 示例 | 快速体验 Excel 用例和元素操作 |
| UI | `bdd_ui` | Feature → Steps → Flows/Factory → Page Objects | 业务可读的 UI 验收自动化 |
| UI | `pytest_ui` | Tests → Flows → Factory → Page Objects | 大型纯 pytest UI 项目 |
| SQL | `sql` | Tests → SQL Service/Repository → Database Gateway | 数据校验、ETL、报表和数据库专项测试；当前为未启用的扩展项目 |

三套 API 和三套 UI Demo 的重复用例、数据工厂是有意保留的，用于展示同一业务在不同自动化模式中的实现方式。公共 HTTP、WebSocket、SSE、MCP、gRPC，以及 Mango Mock 的通用 Repository、Page Object 和 Flow 位于 `auto_tests/common/mango_mock/`。

### 应该选择哪个项目

| 你的情况 | 推荐项目 | 原因 |
|---|---|---|
| 刚开始学习 API 自动化，或项目只有少量 HTTP 接口 | `simple_api` | 目录少、调用链短，容易理解和维护；不需要引入 Feature 与 Steps |
| 小型 UI 项目，主要通过 Excel 管理用例和元素 | `simple_ui` | 数据驱动直接，适合快速覆盖页面操作和元素能力 |
| 产品、测试、开发需要共同评审自然语言场景 | `bdd_api` / `bdd_ui` | 中文 Gherkin 可以作为业务规格和自动化用例的共同文档 |
| 项目强调验收测试、需求追踪，或业务规则经常由非开发角色确认 | `bdd_api` / `bdd_ui` | Feature、Scenario 和 Steps 能清晰表达“前置条件—操作—预期结果” |
| API 项目规模较大，存在多个业务域、复杂数据准备或跨协议流程 | `pytest_api` | Services/Workflows、Factory、Repository 分层更适合长期演进和多人并行开发 |
| UI 项目规模较大，页面多、流程长，需要稳定的 Page Object 和业务 Flow | `pytest_ui` | 测试、流程、数据和页面行为边界明确，重构成本更低 |
| 主要验证数据库、ETL、数据迁移、报表或跨库一致性 | `sql` | 应围绕 Database Gateway、Repository 和数据断言建设；当前需要先补充可收集用例并在注册表启用 |

选择 BDD 的关键不是“用例数量多”，而是团队是否需要用 Gherkin 共同描述和评审业务。如果测试主要由熟悉 Python 的自动化团队维护，并且包含大量参数化、复杂 fixture 或跨系统编排，通常优先选择 `pytest_api` 或 `pytest_ui`。如果只是小项目，不建议为了形式增加 BDD 的 Feature/Steps 维护成本，直接选择 `simple_api` 或 `simple_ui`。

## 项目结构

```text
mango_pytest/
├── auto_tests/
│   ├── common/mango_mock/       # Mango Mock 公共协议和业务基础能力
│   ├── api/
│   │   ├── simple_api/          # 轻量 API Demo
│   │   ├── bdd_api/             # BDD API Demo
│   │   └── pytest_api/          # 大项目纯 pytest API Demo
│   ├── ui/
│   │   ├── simple_ui/           # 轻量 UI Demo
│   │   ├── bdd_ui/              # BDD UI Demo
│   │   └── pytest_ui/           # 大项目纯 pytest UI Demo
│   ├── other/sql/               # 其他类型项目预留目录
│   └── project_registry.py      # 唯一项目与环境注册入口
├── core/                        # 执行、API、UI、DAL、数据源等公共能力
├── web_console/                 # 本地 Web 测试控制台
├── tests/                       # core 框架自身测试
├── docs/                        # 架构、指南、方案和长期维护资源
├── local_packages/              # 芒果内部 Python wheel
├── artifacts/                   # 本地运行产物，默认不提交
├── main.py                      # 命令行统一入口
├── pytest.ini
├── requirements.txt
└── requirements-local.txt
```

## 安装

### 1. 环境要求

- Python 3.10+
- Git
- UI 自动化需要可用的 Chromium、Edge、Firefox、WebKit，或由 Playwright 安装的浏览器
- 示例默认访问 [Mango Mock 测试靶场](http://160.202.231.91:20017)，需要能从本机访问对应服务

以下命令以 macOS/Linux 为例。Windows 可用 `py -3.10 -m venv .venv` 创建环境，并将命令中的 `.venv/bin/python` 替换为 `.\.venv\Scripts\python.exe`；完整图文步骤见[在线帮助文档](http://160.202.231.91:36696/pages/mango-pytest/deploy.html)。

### 2. 获取项目并创建虚拟环境

```bash
git clone https://gitee.com/mao-peng/mango_pytest.git
cd mango_pytest
python3.10 -m venv .venv
```

### 3. 安装依赖

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt -r requirements-local.txt
```

`requirements.txt` 管理开源三方依赖；`requirements-local.txt` 只安装 `local_packages/` 中的 `mangotools` 和 `mangoautomation` wheel。请勿单独从 PyPI 安装这两个内部包，PyPI 上是旧实现。

`requirements-dev.txt` 单独管理 gRPC 代码生成工具，日常运行测试无需安装。需要修改 `.proto` 并重新生成代码时，再执行：

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
```

首次运行 UI 自动化时，可安装 Playwright 浏览器：

```bash
.venv/bin/python -m playwright install chromium
```

如使用本机浏览器，也可以在 Web Console 的“本次执行配置”中临时选择浏览器类型或填写浏览器可执行文件路径，不会修改项目配置文件。

## 命令行测试

所有命令都应使用项目 `.venv`。当前六个 Demo 只注册 `test` 环境，环境列表以 `auto_tests/project_registry.py` 为唯一入口。

```bash
# 查看所有已注册项目及其可用环境
.venv/bin/python main.py --list-projects

# 运行轻量 API Demo
ENV=test .venv/bin/python main.py --project simple_api

# 运行 BDD API Demo
ENV=test .venv/bin/python main.py --project bdd_api

# 运行纯 pytest API Demo
ENV=test .venv/bin/python main.py --project pytest_api

# 运行 UI Demo
ENV=test .venv/bin/python main.py --project simple_ui
ENV=test .venv/bin/python main.py --project bdd_ui
ENV=test .venv/bin/python main.py --project pytest_ui

# 向 pytest 透传 marker、详细度等参数
ENV=test .venv/bin/python main.py --project bdd_api -- -m smoke -q

# 只收集全部已启用 Demo，不执行用例
ENV=test .venv/bin/python main.py --project all --collect-only -q

# 运行 core 框架自身测试
ENV=test .venv/bin/python -m pytest
```

项目配置来自各 Demo 的 `config/.env.test`。用例代码不应写死环境地址；Web Console 允许在单次执行时临时覆盖注册表明确开放的配置，临时值不会回写 `.env` 或源码。

## 使用 Web Console 测试

### 启动

```bash
.venv/bin/python -m web_console
```

服务默认监听 `http://127.0.0.1:8765`，不会自动启动或打开浏览器。需要修改端口时：

```bash
.venv/bin/python -m web_console --port 9000
```

### 使用流程

1. 打开控制台首页，从已注册项目中选择一个 Demo。
2. 首次进入项目时执行“重新收集”，控制台会解析 pytest 测试方法和 BDD Feature/Scenario。
3. 在左侧目录树选择 `.py` 或 `.feature` 文件，右侧直接查看源码和用例标签。
4. 可运行整个项目、一个测试文件，或点击源码左侧的执行按钮运行单条用例。
5. 执行前选择项目已注册的环境，并按需临时修改服务地址、超时、浏览器、无头模式、Trace、元素自愈等开放配置。
6. 执行期间查看实时日志；结束后页面会自动切换到结构化测试结果。
7. 在结果中查看业务层级、Case 信息、测试数据、数据血缘、请求/响应、UI 操作、日志、截图、Fixture 前后置和全部附件。
8. “最近执行”默认加载本地最近 20 条记录，继续向下滚动可加载更早的历史；也可以停止运行中的任务或重新执行历史任务。

控制台直接解析每次运行的 `allure-results`，查看结构化结果不要求预先生成 Allure HTML。完整功能、安全边界、API 和产物说明见 [Web Console 使用指南](docs/guides/web-console.md)。

## 测试产物

全部临时文件统一写入 `artifacts/`，该目录默认加入 `.gitignore`：

```text
artifacts/
├── reports/
│   └── runs/{run_id}/
│       ├── stdout.log
│       ├── events.ndjson
│       ├── junit.xml
│       ├── summary.json
│       └── allure-results/
├── downloads/
├── screenshots/
├── generated_cases/
└── temp/
```

Web 控制台的执行历史保存在 `artifacts/temp/web_console/web_console.sqlite3`，收集缓存位于同目录下的 `collections/`；本地历史不依赖 MySQL。删除 `artifacts/` 前，请先备份需要保留的报告、附件和历史记录。

需要长期维护的 Excel、图片或模板应放在项目约定的数据目录中，不要放入 `artifacts/`。当前 Demo 的共用元素表位于 `core/sources/workbooks/mock_ui/`；文档图片与二维码位于 `docs/assets/images/`。

## 接入芒果测试平台执行

本地调试好的 MangoPytest 项目，可以提交到 Git 仓库后，在芒果测试平台配置仓库同步、项目产品绑定和测试目录，再通过在线执行器运行并查看平台报告，也可纳入定时任务。

- [平台在线 Demo](http://160.202.231.91:35966/#/index/home)
- [测试平台 Pytest 接入流程](http://160.202.231.91:36696/pages/单元自动化/base-flow.html)

本地 Web Console 与平台执行是两条运行入口：平台侧需单独准备执行器依赖、账号、环境及网络访问；本地 SQLite 历史不会自动上传为平台报告。


## 开发与贡献

欢迎提交 Issue、改进文档、补充协议能力或提交 Pull Request。参与开发前请先阅读项目根目录的 `AGENTS.md`，其中说明了六类 Demo 的分层边界、数据创建规范、日志规范和内部包使用约束。

提交改动前建议至少执行：

```bash
ENV=test .venv/bin/python -m pytest
ENV=test .venv/bin/python main.py --project all --collect-only -q
```

更多资料：

- [项目架构](docs/architecture/)
- [使用指南](docs/guides/)
- [AI 元素定位使用指南](docs/guides/AI元素定位使用指南.md)
- [AI 定位提示词编写规范](docs/guides/AI定位提示词编写规范.md)
- [内部包升级记录与已知失败](docs/guides/内部包升级记录.md)
- [AI 元素定位接入方案](docs/plans/AI元素定位接入方案.md)
- [重构与演进方案](docs/plans/)
- [开源许可证](LICENSE)

## 开源协议与使用要求

### 开源许可证

本仓库使用 [GNU GPL-3.0](LICENSE)，与芒果测试平台主仓库的许可证分别说明。修改、分发及再发布时，请遵守完整许可证，保留适用的版权与许可声明，并履行相应的源码提供义务。

GPL-3.0 本身不是“禁止商业用途”的许可证，收费分发也需要遵守协议条件，参见 [GNU 官方说明](https://www.gnu.org/licenses/gpl-faq.en.html#DoesTheGPLAllowMoney)。

### 作者的开源诉求

- 希望项目用于**企业内部自动化建设、学习和技术交流**，帮助大家理解并实践 API/UI 自动化。
- **不希望项目被用于收费教学、二次销售等以项目本身牟利的活动。**
- 二次开发请尊重原作者，保留项目名称、作者署名、原始版权、许可证和 README 中的联系方式及帮助文档入口。
- 欢迎 Fork、分享真实实践、提交 Issue 和 Pull Request，不要将原项目包装为完全独立原创的作品。

以上是作者对项目使用和社区协作的倡议，与 GPL-3.0 条文本身分开说明；授权及义务以完整许可证和适用约定为准。

### 运行与数据使用

- 使用项目虚拟环境，并通过 `requirements.txt` 与 `requirements-local.txt` 安装配套依赖，不单独从 PyPI 安装旧版内部包。
- Demo 用于测试环境和测试数据。换成自己的服务前，请确认目标地址、账号、用例副作用及清理策略，不要直接对生产环境全量执行示例。
- 密码、访问令牌、AI 密钥及真实业务数据不要提交到公开仓库；报告和原始日志也可能包含请求与响应，分享前请脱敏。
- 需要升级或清理本地产物时，先备份自己的测试配置、长期维护的数据文件及需要保留的运行记录。

## 联系作者与交流群

| 方式 | 联系信息 |
| --- | --- |
| 微信 | `mpeng0813`，添加时备注 **“芒果测试平台 / MangoPytest”** |
| 邮箱 | [729164035@qq.com](mailto:729164035@qq.com) |
| Gitee | [mao-peng/mango_pytest](https://gitee.com/mao-peng/mango_pytest) |
| GitHub | [maopengg/MangoPytest](https://github.com/maopengg/MangoPytest) |
| 使用文档 | [MangoPytest 启动与使用](http://160.202.231.91:36696/pages/mango-pytest/deploy.html) |

扫码添加作者或加入交流群。群二维码失效时，请添加作者后申请邀请；群内主要交流项目使用、自动化实践和技术问题。

<p align="center">
  <img src="docs/assets/images/author-wechat.jpg" width="280" alt="作者微信二维码">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="docs/assets/images/wechat-group.jpg" width="260" alt="芒果测试平台交流群二维码">
</p>

反馈问题时请附上代码版本、操作系统、Python 版本、运行命令、复现步骤和脱敏后的完整错误。功能建议请说明业务场景和预期结果；维护精力有限，回复和实现时间会结合实际情况安排。

## 支持开源项目

如果这个项目对你有帮助，欢迎 **Star、分享实践、完善文档或贡献代码**。愿意请作者喝杯咖啡的话，可以使用下面的微信收款码；支持完全自愿。感谢每一份反馈与贡献。

<p align="center">
  <img src="docs/assets/images/wechat-payment.jpg" width="460" alt="自愿支持项目的微信收款码">
</p>

---

版权所有 © 2022–至今 芒果味。
