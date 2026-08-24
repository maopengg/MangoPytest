# Mango Pytest Web 控制台

## 启动

```bash
.venv/bin/python -m web_console
```

默认地址为 `http://127.0.0.1:8765`。服务只允许绑定 `127.0.0.1` 或 `localhost`，启动命令不会主动打开浏览器。

可指定端口：

```bash
.venv/bin/python -m web_console --port 9000
```

## 使用流程

1. 在首页选择一个已注册项目。
2. 首次进入或收集格式升级后点击“重新收集”，生成带版本的结构化用例清单。
3. 左侧按目录树选择 `.py` / `.feature` 文件，右侧直接查看源码；源码中测试方法或 BDD 场景左侧可直接执行，并展示 Case ID 与标签。
4. 可运行整个项目、测试文件、单条 pytest node ID 或单个 BDD Feature。一个 pytest 绑定文件包含多个 Feature 时，控制台只执行当前 Feature 映射出的精确节点。
5. 从项目注册代码明确开放的运行配置中选择环境，按需修改“本次执行配置”，再设置 markers、并发数和失败重跑次数。
6. 执行时默认查看实时日志；任务结束 0.5 秒后自动切换到结构化测试结果。

用例搜索覆盖显示名称、Case ID、pytest node ID 和标签。目录树只默认展开包含用例的分支；没有用例的配置、数据工厂和辅助代码目录默认收起。BDD 项目按 Feature 文件而不是 Python 绑定文件组织用例。

## 结构化执行结果

详情页直接解析每次运行的 `allure-results/`，不需要额外执行 `allure generate`：

- 概览：通过、失败、异常、跳过、执行时间和总耗时。
- 用例树：默认按 `项目 → Epic → Feature → Story（可选）→ Case` 展示业务层级，也可切换为 `Parent Suite → Suite → Case` 文件层级；支持逐级折叠、状态过滤与搜索。没有 Story 的用例直接归入 Feature，未设置业务标签的轻量用例归入项目下的“未分类”。
- 用例详情：Epic/Feature/Story、tags、severity、参数和失败堆栈。
- 执行过程：嵌套 `allure.step`、pytest fixture 前后置及各自耗时。
- 测试证据：Case 信息、测试数据、API/协议请求与响应、UI 操作明细、日志、截图和数据工厂血缘关系。
- 附件：日志、JSON、文本、截图等在用例详情中直接预览；完整原始文件统一从“产物”页签下载。

API 请求体和响应体中的业务 JSON 保留原始 key 与原始层级；只有平台自身记录的固定字段使用中文标签。实时 pytest 日志和全部原始产物保留为独立页签。用例没有显式记录
`allure.step` 时，页面仍会展示 Allure 自动采集的 fixture、标签和附件；新增步骤后无需修改控制台即可自动展示。

生产环境默认需要在执行面板输入项目 ID 二次确认。

运行环境以 `auto_tests/project_registry.py` 的 `environments` 为唯一入口，每个环境再关联项目内的配置文件：

```python
"environments": {
    "test": {
        "label": "Mango Mock 测试环境",
        "config_file": "config/.env.test",
    }
}
```

控制台不会扫描文件名来猜测环境。项目只声明一个环境时，页面显示固定配置而不是下拉框；未声明的 `dev/pre/prod` 即使存在历史文件也不会显示，API 同样拒绝执行。

项目还可以在注册表中通过 `runtime_options` 声明允许临时覆盖的配置。控制台只展示这些字段，并按照 URL、整数范围、布尔值或枚举进行服务端校验。API 项目当前支持临时覆盖服务地址和请求超时；UI 项目支持测试页面地址、浏览器类型、浏览器可执行文件路径、无头模式、操作超时，以及已实现 Trace 的项目中的 Trace 开关。这些值只注入本次 pytest 子进程，不改动 `.env` 或源码，并随执行记录保存供重跑复用。

## 数据和产物

```text
artifacts/
├── reports/runs/{run_id}/
│   ├── stdout.log
│   ├── events.ndjson
│   ├── junit.xml
│   ├── summary.json
│   └── allure-results/
└── temp/web_console/
    ├── web_console.sqlite3
    └── collections/
```

`artifacts/` 整体位于 `.gitignore`，历史记录仅保存在本地。

## 安全边界

- 前端只能执行项目注册表中的项目。
- 文件和 node ID 必须来自项目目录内的 `test_*.py`；Feature 必须来自项目内的 `.feature`，并解析为收集清单中的精确 pytest node ID 后才能执行。
- 执行命令不经过 shell，页面不能提交任意 pytest 参数。
- 源码查看仅允许项目内的 `.py` 和 `.feature`，拒绝路径穿越和环境文件。
- 取消任务会终止 pytest 进程组，包括 xdist worker 和 UI 浏览器子进程。
- 临时配置只能使用项目注册表声明的字段，不能借此注入 `PYTHONPATH` 等任意环境变量。
- 本地调试结果保留请求、响应和日志原值，包括 token、password 与 authorization。

## API

FastAPI 自动文档位于 `http://127.0.0.1:8765/docs`。主要接口包括项目列表与收集、用例树、创建/停止/重跑任务、历史记录、SSE 日志和受控产物下载。
