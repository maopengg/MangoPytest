# Web Console

Web Console 是本地 pytest 操作界面，提供项目浏览、用例收集、任务执行与取消、实时日志、Allure 报告和产物访问。协议客户端、pytest 命令构建及公共 UI Runtime 继续复用 `core/`，控制台不实现具体产品业务。

## 目录

```text
web_console/
├── __init__.py                 # 对外提供 create_app
├── __main__.py                 # python -m web_console
├── app.py                      # 应用及生命周期装配
├── config.py                   # 控制台配置
├── api/
│   ├── dependencies.py         # 请求使用的服务容器
│   ├── middleware.py           # 来源检查、静态资源缓存策略
│   ├── presenters.py           # 对外运行记录脱敏
│   └── routes/
│       ├── pages.py            # HTML 页面
│       ├── projects.py         # 项目、收集、用例树和源码
│       ├── runs.py             # 创建、查询、取消、重跑、SSE
│       └── reports.py          # 报告、预览和下载
├── schemas/
│   └── runs.py                 # 执行请求与参数模型
├── services/
│   ├── collection.py           # pytest 收集与清单缓存
│   ├── runs.py                 # 任务调度、子进程、并发与取消
│   ├── events.py               # 事件文件写入与增量读取
│   ├── allure.py               # Allure 原始结果归一化
│   └── artifacts.py            # 失败信息、自愈统计与产物访问范围
├── repositories/
│   └── runs.py                 # SQLite 执行记录存储
├── plugins/
│   └── pytest_collection.py    # 收集子进程加载的 pytest 插件
├── templates/
│   ├── base.html
│   └── pages/{dashboard,project,run_detail}.html
└── static/
    ├── css/
    │   ├── app.css             # 样式导入入口
    │   ├── base.css
    │   ├── components.css
    │   └── pages/{dashboard,project,run_detail}.css
    └── js/
        ├── app.js              # 页面初始化和模板事件处理函数注册
        ├── common/{api,dom}.js
        ├── pages/{dashboard,project,run_detail}.js
        └── reports/{allure,evidence,lineage}.js
```

Python 包目录均包含 `__init__.py`，各模块从具体实现路径导入，不保留旧路径转发文件。

## 调用关系

`app.py` 创建配置、Catalog、Repository 和各项 Service，通过 `api/dependencies.py` 中的容器提供给路由。路由处理 HTTP 参数、状态码和响应，任务与文件操作进入 Service；数据库访问进入 Repository。

用例收集由 `CollectionService` 启动短生命周期 pytest 子进程，并通过 `-p web_console.plugins.pytest_collection` 输出清单。执行任务由 `RunService` 调用 `core.execution`，同一项目串行，UI 任务额外限制为全局串行。应用退出时取消并回收未完成任务。

运行记录对外通过 `api/presenters.py` 脱敏。执行链路保留内部原值，重跑从记录恢复参数。事件服务负责写入 `events.ndjson`、`stdout.log`，路由将事件迭代器转换为 SSE。报告及文件路径由 `ArtifactService` 解析，路由负责 `FileResponse`。

前端使用浏览器原生 ES Modules，不需要 Node 构建。页面状态保留在对应模块中，跨模块调用显式导入。`js/app.js` 等 DOM 就绪后初始化当前页面，并仅将模板或动态 HTML 使用的处理函数注册到 `window`；模板只提供页面结构和 JSON 上下文。`css/app.css` 按入口顺序加载基础、公共组件和页面样式。

## 启动

在仓库根目录执行：

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m web_console
# 指定本机端口
.venv/bin/python -m web_console --port 9000

# 也支持 IDE 直接运行文件，启动参数与模块入口一致
.venv/bin/python web_console/app.py --port 9000
```

直接运行 `app.py` 时会根据文件位置解析仓库根目录，不要求当前工作目录位于仓库内；无需手动配置 `PYTHONPATH`。

默认地址为 `http://127.0.0.1:8765`。CLI 只允许监听本机，当前控制台没有远程访问认证。程序入口仍可使用 `from web_console import create_app`；测试可向 `create_app(settings)` 注入临时路径和数据库。

页面 URL、`/api/projects`、`/api/runs` 等 API 路径保持原有契约；完整接口见本机 `/docs`。静态资源入口为 `/static/css/app.css` 和 `/static/js/app.js`。

## 数据和产物

```text
runtime/
├── cache/web_console/
│   ├── web_console.sqlite3
│   └── collections/
└── reports/runs/{run_id}/
    ├── stdout.log
    ├── events.ndjson
    ├── junit.xml
    ├── summary.json
    └── allure-results/
```

路径由 `WebConsoleSettings` 与公共 Runtime 解析，`MANGO_PYTEST_RUNTIME_DIR` 可覆盖运行根目录。目录和数据库结构未因模块重构而改变，无需搬迁既有历史记录。运行产物不提交。

来源检查阻止外部网页写入；可执行项目和临时参数由项目注册表限定；执行命令不经过 shell；源码和产物访问限定在对应项目或运行目录内。报告包含本地调试原始证据，分享前应确认其中不含敏感数据。

## 测试

```bash
# 后端、报告、静态资源依赖，以及临时项目的真实子进程执行
ENV=test .venv/bin/python -m pytest tests/web_console -q

# 真实浏览器交互验证：进程内 HTTP 客户端，不启动常驻服务
ENV=test .venv/bin/python -m pytest tests/integration/ui/test_web_console.py -q

# 公共框架离线回归
ENV=test .venv/bin/python -m pytest tests \
  -m 'not ai_e2e and not ai_smoke and not browser_e2e' -q
```

测试使用临时样例项目、数据库和报告，不连接实际业务环境。浏览器测试标记为 `browser_e2e`，需要可用的 Chrome 或 Playwright Chromium，并在完成后关闭浏览器。

## 新增功能放置位置

- 新增 HTTP 接口放到相应 `api/routes/`，请求模型放 `schemas/`；路由不直接执行 SQL、启动子进程或拼接产物文件路径。
- 新增收集、执行或报告规则放到对应 `services/`；持久化访问放 `repositories/`。`app.py` 只增加依赖和路由装配。
- 新增页面放 `templates/pages/`，页面行为和样式分别放 `static/js/pages/`、`static/css/pages/`；报告渲染放 `static/js/reports/`，共享请求与 DOM 能力放 `common/`。
- 新增跨模块前端调用使用显式 import，避免通过 `window` 共享页面状态。新增模板事件处理函数在 `js/app.js` 注册。
- 修改收集插件时同步验证子进程中的插件加载路径；改变清单结构时再升级 `COLLECTION_SCHEMA_VERSION`。
- 功能变更补充公共框架测试，真实产品的专属检查仍留在对应 `auto_tests/` 项目下。
