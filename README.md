# Mango Pytest

多项目 pytest 自动化示例仓库，覆盖 API、UI、BDD、数据工厂和多协议测试。Mango Mock 统一使用外部项目 `/Users/mango/code/mango-mock` 发布的服务，本仓库不再维护第二套 Mock 实现。

## 项目布局

```text
mango_pytest/
├── auto_tests/
│   ├── common/mango_mock/       # HTTP/WebSocket/SSE/MCP/gRPC 公共客户端
│   ├── api/
│   │   ├── simple_api/          # 轻量纯 pytest，16 条
│   │   ├── bdd_api/             # 中文 Gherkin BDD，165 条
│   │   └── pytest_api/          # 大项目五层纯 pytest，165 条
│   ├── ui/
│   │   ├── simple_ui/
│   │   ├── bdd_ui/
│   │   └── pytest_ui/
│   ├── other/sql/               # 尚无 pytest Case，注册表中禁用
│   └── project_registry.py
├── core/                        # 框架公共能力，DAL 位于 core/dal/
├── web_console/                 # 本地 Web 自动化控制台
├── tests/                       # 只测试 core，DAL Case 位于 tests/test_dal/
├── docs/
│   ├── architecture/
│   ├── guides/
│   ├── plans/
│   └── assets/
├── local_packages/              # 芒果内部包 wheel
├── artifacts/                   # 运行产物，整体忽略
├── main.py
└── pytest.ini
```

## 三种 API 自动化方式

| 项目 | 调用链 | 适用场景 |
|---|---|---|
| `simple_api` | Tests → Fixture → Factory/Repository → HTTP | 入门、小型项目、少量接口 |
| `bdd_api` | Feature → Steps → Factory → Repositories → 公共协议 | 业务共同评审、验收测试 |
| `pytest_api` | Tests → Services/Workflows → Factory → Repositories → 公共协议 | 大项目、多业务域、多协议编排 |

三套 Case 和数据工厂有意独立，用户按团队需求选择一种；只有底层协议客户端统一复用 `auto_tests/common/mango_mock/`。

## 环境与依赖

必须使用项目 `.venv`。`mangotools`、`mangoautomation` 只从 `local_packages/` 安装，禁止从 PyPI 安装旧版本。

```bash
.venv/bin/python -m pip install -r requirements.txt -r requirements-local.txt
```

默认环境是 `test`；`prod` 必须显式指定。

## 运行

```bash
# 查看注册项目
.venv/bin/python main.py --list-projects

# 运行一个项目
ENV=test .venv/bin/python main.py --project pytest_api

# 给 pytest 透传参数
ENV=test .venv/bin/python main.py --project bdd_api -m smoke -q

# 独立收集全部已启用 Demo（每个项目使用自己的 rootdir）
ENV=test .venv/bin/python main.py --project all --collect-only -q

# 根 pytest 只验证 core，避免不同 Demo 的 fixture/plugin 冲突
ENV=test .venv/bin/python -m pytest
```

## Web 控制台

```bash
ENV=test .venv/bin/python -m web_console
```

然后由用户打开 `http://127.0.0.1:8765`。控制台不会自动打开浏览器，只监听本机地址，支持收集和浏览用例、执行项目/文件/单用例、实时日志、停止任务、失败重跑、JUnit/Allure 产物和历史记录。

详细说明见 [Web 控制台指南](/Users/mango/code/mango_pytest/docs/guides/web-console.md)。

## 产物规则

所有运行时文件写入并忽略：

```text
artifacts/
├── reports/
├── downloads/
├── screenshots/
├── generated_cases/
└── temp/
```

需要长期维护的 Excel、图片和模板放在 `docs/assets/`。当前 API/UI 功能用例工作簿位于 `docs/assets/test-cases/`。

更多资料见 [架构文档](/Users/mango/code/mango_pytest/docs/architecture)、[使用指南](/Users/mango/code/mango_pytest/docs/guides) 和 [改造方案](/Users/mango/code/mango_pytest/docs/plans)。
