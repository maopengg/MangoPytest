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
2. 首次进入时点击“重新收集”，生成结构化用例清单。
3. 选择运行整个项目、测试文件或单条 pytest node ID。
4. 从项目注册代码明确开放的运行配置中选择环境，再设置 markers、并发数和失败重跑次数。
5. 在执行详情页查看实时日志、JUnit 统计和报告产物。

## 结构化执行结果

详情页直接解析每次运行的 `allure-results/`，不需要额外执行 `allure generate`：

- 概览：通过、失败、异常、跳过、执行时间和总耗时。
- 用例树：按 Suite 展示用例名称、状态和耗时，支持状态过滤与搜索。
- 用例详情：Epic/Feature/Story、tags、severity、参数和失败堆栈。
- 执行过程：嵌套 `allure.step`、pytest fixture 前后置及各自耗时。
- 附件：日志、JSON、文本、截图等，可直接预览或下载。

实时 pytest 日志和全部原始产物保留为独立页签。用例没有显式记录
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

控制台不会扫描文件名来猜测环境，也不允许用户输入域名。项目只声明一个环境时，页面显示固定配置而不是下拉框；未声明的 `dev/pre/prod` 即使存在历史文件也不会显示，API 同样拒绝执行。

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
- 文件和 node ID 必须来自项目目录内的 `test_*.py`。
- 执行命令不经过 shell，页面不能提交任意 pytest 参数。
- 源码查看仅允许项目内的 `.py` 和 `.feature`，拒绝路径穿越和环境文件。
- 取消任务会终止 pytest 进程组，包括 xdist worker 和 UI 浏览器子进程。
- 日志对 authorization、token、password、secret 和 cookie 做基础脱敏。

## API

FastAPI 自动文档位于 `http://127.0.0.1:8765/docs`。主要接口包括项目列表与收集、用例树、创建/停止/重跑任务、历史记录、SSE 日志和受控产物下载。
