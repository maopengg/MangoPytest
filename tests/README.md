# 公共框架测试

根 `tests/` 只验证公共框架。目录和测试代码应能直接复用于公司项目，不依赖具体产品的项目注册表、配置类、元素工作簿、业务账号或在线服务。

| 目录 | 验证范围 |
|---|---|
| `architecture/` | Case 元数据契约，以及框架测试不导入业务项目的边界 |
| `runtime/` | 运行路径、配置中的输出目录、日志和旧产物迁移 |
| `execution/` | 命令构建、项目目录与环境解析、结果解析、证据采集和凭据脱敏 |
| `data/` | 公共 Factory、Repository 和数据血缘 |
| `dal/unit/` | DAL 表达式、路径、运算符及 Schema |
| `dal/integration/` | DAL 组件协作；不连接业务服务 |
| `dal/features/` | DAL 的中文 Gherkin 场景及公共步骤 |
| `ui/` | Excel/飞书元素源、模型装配、提示词、自愈统计及浏览器生命周期 |
| `web_console/` | 控制台接口、页面接线、用例收集、报告和存储 |
| `integration/ui/` | 使用真实浏览器的框架及控制台验证，以及需要真实凭据的 AI 网关冒烟 |

分类按被验证的对象判断，不按是否使用 pytest、Mock 或真实环境判断：

| 检查内容 | 归属 |
|---|---|
| 用临时实体验证公共 Factory 基类能创建和清理数据 | 根 `tests/data/` |
| 验证某产品 Factory 的业务字段、默认值或业务清理策略 | 对应 `auto_tests/` 项目的 `tests/` |
| 用临时工作簿验证通用元素解析和运行时装配 | 根 `tests/ui/` |
| 验证某产品的元素 ID、实际工作簿数量或业务页面清单 | 对应 `auto_tests/common/<product>/tests/` |
| 验证通用命令、参数校验和报告解析 | 根 `tests/execution/` 或 `tests/web_console/` |
| 用模拟响应验证某产品的权限、字段同步或状态流转 | 对应 `auto_tests/` 项目的 `tests/`，仍属于业务专属检查 |

其他类型文件的放置规则见根 `AGENTS.md` 的“文件与目录放置规范”。

所有命令在仓库根目录执行，使用 `.venv` 并显式设置 `ENV`。

```bash
# 公共框架离线回归：不启动浏览器、不访问真实 AI 网关
ENV=test .venv/bin/python -m pytest tests -m 'not ai_e2e and not ai_smoke and not browser_e2e' -q

# 定向验证某项公共能力
ENV=test .venv/bin/python -m pytest tests/ui tests/execution -q

# 只收集框架测试，包括需要额外运行条件的集成测试
ENV=test .venv/bin/python -m pytest tests --collect-only -q

# 真实浏览器 + 模拟模型，不调用真实 AI 服务
ENV=test .venv/bin/python -m pytest tests/integration/ui/test_ai_locating.py -q
```

`test_ai_gateway.py` 默认跳过，需要通过环境变量或 CI Secret 注入 `AI_API_KEY` 后定向执行。不要在文档或测试代码中保存真实密钥。

`test_web_console.py` 使用 `browser_e2e` 标记，验证真实浏览器中的页面模块和交互；HTTP 请求由进程内 FastAPI 测试客户端处理，不启动常驻服务。可用 `ENV=test .venv/bin/python -m pytest tests/integration/ui/test_web_console.py -q` 单独运行。

公共 Fixture 位于 `conftest.py`：项目目录和注册表由临时样例生成，控制台使用临时数据库；`ui/conftest.py` 提供临时元素工作簿和产品映射。数据工厂测试使用内存数据库。

具体产品的配置、真实元素工作簿、业务目录和协议编排检查不属于根框架套件，应由对应的 `auto_tests/` 项目单独维护和执行。同步公共框架时不复制某个产品的专属检查。

新增测试按被验证的公共能力归类，Python 包目录补齐 `__init__.py`。产品业务回归以及特定项目的离线检查放在对应的 `auto_tests/` 项目或产品公共目录，不复制到根 `tests/`。
