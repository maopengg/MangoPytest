# 芒果测试平台 — 项目架构

## 1. 项目概述

芒果测试平台（mango_pytest）是一个集 **API + UI** 于一体的多项目自动化测试平台，基于 pytest 生态构建。

| 层级 | 说明 |
|------|------|
| 技术栈 | Python 3.10, pytest 8.x, pytest-bdd, httpx, Playwright, Allure |
| 测试风格 | BDD（中文 Gherkin 语法） |
| 配置管理 | Pydantic Settings + 多环境 .env |
| 并行执行 | pytest-xdist（按模块分配进程） |

### 1.1 目录结构总览

```
qfei_auto_tests/
├── main.py                   # 统一启动入口
├── requirements.txt
├── core/                     # 框架层（所有项目共享）
├── auto_tests/               # 项目层
│   ├── qfei_contract_api/    #   API 自动化测试
│   └── qfei_contract_ui/     #   UI 自动化测试
└── docs/                     # 文档
```

---

## 2. 环境搭建

### 2.1 前置依赖

- Python 3.10+
- Git
- VPN（访问公司内网测试环境）

### 2.2 安装

```bash
git clone <仓库地址>
cd qfei_auto_tests
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 2.3 验证

```bash
# API 项目冒烟测试
ENV=dev .venv/Scripts/python -m pytest ^
  auto_tests/qfei_contract_api/test_cases/migrated/clm/home_page/ -v

# 从 main.py 启动（完整测试）
.venv/Scripts/python main.py
```

---

## 3. 启动流程

```
main.py
  │  指定项目 + 环境
  ▼
MainRun(project_config, pytest_command)
  │  os.environ["ENV"] = "dev"        # 设置项目环境
  │  拼接项目测试路径
  ▼
pytest.main(cmd)
  │  conftest.py 自动发现 steps/ 和 fixtures/
  │  xdist 并行执行
  ▼
Allure 报告生成
```

### 3.1 环境解析优先级

```
ENV 环境变量（命令行或 MainRun 设置）
    ↓ 未设置
DEFAULT_ENV（项目 __init__.py 中定义）
```

每个项目在 `__init__.py` 中声明默认环境：
```python
# auto_tests/qfei_contract_api/__init__.py
PROJECT_NAME = "qfei_contract_api"
PROJECT_TYPE = AutoTestTypeEnum.API
DEFAULT_ENV = "dev"
```

---

## 4. 框架层（core/）

### 4.1 APIClient — 统一 HTTP 客户端

文件：`core/api/client.py`

```python
from core.api.client import APIClient

client = APIClient(
    base_url="https://dev-contract.qtech.cn",
    headers={"Content-Type": "application/json"},
)
response = client.post("/api/endpoint", json={"key": "value"})
print(response.status_code)  # int
print(response.data)         # dict
print(response.elapsed_ms)   # float
```

特性：
- 基于 httpx，支持连接池复用
- 内置请求/响应拦截器
- 自动重试机制（`retry_count`, `retry_delay`）
- `raise_on_error=False` 禁用 4xx/5xx 异常抛出
- 文件上传：`client.upload(path, file_path, data)`

### 4.2 BDD 通用断言步骤

文件：`core/api/bdd_steps.py`

每个 Feature 文件都可以直接使用的内置断言：

| Gherkin 步骤 | 说明 |
|---|---|
| `响应状态码为 {code:d}` | 验证 HTTP 状态码 |
| `code 为 {expected:d}` | 验证 JSON body.code |
| `success 为 true` | 验证 JSON body.success |
| `{path} 为 {expected}` | 通用路径等于断言 |
| `{path} 不为 {expected:d}` | 路径不等于断言 |
| `{path} 包含 {expected}` | 路径包含子串 |
| `{path} 不为空` | 验证列表非空 |
| `{path} 存在` | 验证路径不为 null |
| `{path} 大小为 {size:d}` | 验证列表大小 |
| `响应数据匹配表格:` | 表格数据验证 |

文件：`core/dal/bdd_steps.py`

| Gherkin 步骤 | 说明 |
|---|---|
| `{path} 应该等于 {expected}` | DAL 路径断言 |
| `{path} 应该包含 {expected}` | DAL 包含断言 |
| `{path} 应该为 true` | DAL 布尔断言 |
| `{path} 应该大于 {value}` | DAL 数值比较 |

### 4.3 DAL 数据断言语言

文件：`core/dal/`

自定义的声明式断言 DSL，在 Feature 文件中通过 `表格` 或 `表达式` 验证 JSON 响应：

```gherkin
# 表格断言
那么 响应数据匹配表格:
  | id | name  |
  | 1  | Alice |

# 表达式断言
那么 响应数据匹配:
  success = true
  data.list.size > 0
```

### 4.4 Allure 报告

APIClient 每次请求自动通过 `api_allure_logger` 装饰器将请求/响应详情写入 Allure 报告。

报告生成：
```bash
# 运行测试时自动生成 Allure 数据
pytest ... --alluredir=./report/tmp --clean-alluredir

# 生成 HTML 报告
allure generate ./report/tmp -o ./report/html --clean

# 查看报告
allure serve ./report/tmp
```

### 4.5 告警通知

文件：`core/utils/notice.py`

```python
from core.utils.notice import NoticeMain

notice = NoticeMain("project_name", "项目显示名", "dev")
notice.email_alert("测试完成，1 个失败")
notice.wechat_alert("https://qyapi.weixin.qq.com/...")
```

---

## 5. 项目元数据

每个项目在 `auto_tests/项目名/__init__.py` 中声明自身信息：

```python
# auto_tests/qfei_contract_api/__init__.py
PROJECT_NAME = "qfei_contract_api"      # 目录名
PROJECT_TYPE = AutoTestTypeEnum.API      # API 或 UI
DEFAULT_ENV = "dev"                      # 默认测试环境
PROJECT_DISPLAY_NAME = "智书合同API"     # 报告显示名
```

---

## 6. main.py 启动说明

```python
MainRun(
    project_config={
        'project': PROJECT_NAME,
        'test_environment': EnvironmentEnum.DEV,  # dev / test / pre / prod
        'type': AutoTestTypeEnum.API,
    },
    pytest_command=[
        '-s',                                  # 捕获 print 输出
        '-v',                                  # 详细结果
        '-W',
        'ignore:Module already imported:pytest.PytestWarning',  # 忽略重复导入警告
        '--alluredir', './report/tmp',         # Allure 输出目录
        "--clean-alluredir",                   # 运行前清空
        '-n 3',                                # 3 进程并行
        '--dist=loadscope',                    # 按模块分配进程
        '-p no:warnings',                      # 屏蔽警告
    ],
)
```

---

## 7. 常见问题

**测试跑不起来？**
- 确认 VPN 已连接
- 确认 `ENV` 环境变量设置正确（`ENV=dev`、`ENV=test` 等）
- 确认 .env.xxx 中 Token 未过期

**新增步骤不生效？**
- 检查是否创建了 `__init__.py`
- conftest.py 会自动发现 `steps/migrated/` 下的所有 `.py` 文件

**Allure 报告没生成？**
- 确认 pytest 命令行包含 `--alluredir`
- 确认已安装 Allure CLI：`allure --version`
