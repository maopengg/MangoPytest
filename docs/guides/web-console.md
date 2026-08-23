# Mango Pytest Web 控制台

## 启动

```bash
ENV=test .venv/bin/python -m web_console
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
4. 选择环境、markers、并发数和失败重跑次数后开始执行。
5. 在执行详情页查看实时日志、JUnit 统计和报告产物。

生产环境默认需要在执行面板输入项目 ID 二次确认。

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
