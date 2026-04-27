# mango_pytest

## 介绍

mango_pytest 是一个集 **API，UI 自动化测试** 于一体的测试平台，采用多种架构模式满足不同场景的测试需求。项目分别包含三个独立的API和三个独立的UI以及一个其他类型的自动化，分别采用不同的设计模式。

### 三种架构模式对比

| 项目 | 架构模式 | 适用场景 | 核心特点 |
|------|---------|---------|---------|
| **api_mock** | 抽象页面对象模式 | 传统 API 测试 | 分层抽象、多环境配置、简洁易用 |
| **bdd_api_mock** | BDD + pytest-factoryboy | 业务驱动测试 | Gherkin 语法、数据库直连、自动清理 |
| **pytest_api_mock** | 五层数据工厂模式 | 复杂数据依赖场景 | Pydantic 实体、依赖自动解决、状态机 |

### 优劣势对比

| 项目 | 优势 | 劣势 | 推荐指数                           |
|------|------|------|--------------------------------|
| **api_mock** | ✅ 学习成本低，快速上手<br>✅ 代码简洁直观<br>✅ 维护简单，适合小团队<br>✅ 与 UI 页面对象模式一致 | ❌ 数据准备逻辑分散<br>❌ 复杂依赖场景代码冗余<br>❌ 缺少数据自动清理机制 | ⭐⭐⭐⭐⭐<br>（推荐新手,文档只提供这个模式的帮助文档） |
| **bdd_api_mock** | ✅ 业务人员可读可写<br>✅ 中文描述测试场景<br>✅ 数据库直连，数据准备快<br>✅ pytest-factoryboy 自动注册 fixtures | ❌ 学习曲线陡峭<br>❌ 需要维护 Gherkin 和代码两套描述<br>❌ 执行速度相对较慢<br>❌ 占位符解析增加复杂度 | ⭐⭐⭐⭐<br>（推荐业务驱动团队）             |
| **pytest_api_mock** | ✅ 强类型校验（Pydantic）<br>✅ 复杂依赖自动解决<br>✅ 数据流向清晰（to_api_payload）<br>✅ 状态机管理业务流程<br>✅ 血缘追踪数据关系 | ❌ 学习成本最高<br>❌ 代码量较大<br>❌ 过度设计风险<br>❌ 不适合简单场景 | ⭐⭐⭐<br>（推荐复杂业务场景）              |

### 选型建议

- **新手/快速上手** → 选择 **api_mock**（抽象页面对象模式）
- **业务人员参与/需要中文描述** → 选择 **bdd_api_mock**（BDD 模式）
- **复杂数据依赖/追求极致可维护性** → 选择 **pytest_api_mock**（五层数据工厂模式）

---

## 项目架构对比

### 三种架构模式详解

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        三种 API 自动化测试架构对比                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  【api_mock - 抽象页面对象模式】                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │ Test Cases  │ →  │  Abstract   │ →  │ API Manager │ →  │   HTTP      │  │
│  │   (L5)      │    │   (L4)      │    │   (L3)      │    │   Client    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│       测试用例         业务抽象层          接口管理层          通信层         │
│                                                                             │
│  特点：简洁直观，适合快速上手，业务逻辑封装在 Abstract 层                        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  【bdd_api_mock - BDD + pytest-factoryboy】                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Feature   │ →  │   Steps     │ →  │  Factories  │ →  │  Entities   │  │
│  │  (Gherkin)  │    │ (步骤定义)   │    │(数据工厂)    │    │ (SQLAlchemy)│  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│      中文场景描述       步骤实现           自动注册 fixtures    ORM 实体      │
│                              ↓                                            │
│                         ┌─────────────┐                                   │
│                         │ Repositories│                                   │
│                         │ (数据访问层) │                                   │
│                         └─────────────┘                                   │
│                                                                             │
│  特点：业务人员可读可写，使用 Gherkin 中文语法，数据库直连                        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  【pytest_api_mock - 五层数据工厂模式】                                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │ Test Cases  │ →  │  Scenarios  │ →  │  Entities   │ →  │  Builders   │  │
│  │   (L5)      │    │   (L4)      │    │   (L3)      │    │   (L2)      │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│       用例层           场景层              实体层              构造器层        │
│                                                                   ↓        │
│                                                            ┌─────────────┐ │
│                                                            │ API Manager │ │
│                                                            │   (L1)      │ │
│                                                            └─────────────┘ │
│                                                                             │
│  特点：Pydantic 强类型，to_api_payload() 数据流向，依赖自动解决，状态机         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 项目结构

```
mango_pytest/
├── auto_tests/                    # 自动化测试主目录
│   ├── api_mock/                  # 【抽象页面对象模式】API 测试
│   │   ├── abstract/              # 业务抽象层
│   │   ├── test_cases/            # 测试用例
│   │   ├── config/                # 多环境配置
│   │   └── README.md              # 项目文档
│   │
│   ├── bdd_api_mock/              # 【BDD 模式】行为驱动测试
│   │   ├── features/              # Gherkin 特性文件
│   │   ├── steps/                 # 步骤定义
│   │   ├── factories/             # pytest-factoryboy 数据工厂
│   │   ├── entities/              # SQLAlchemy 实体
│   │   ├── repos/                 # Repository 数据访问
│   │   └── README.md              # 项目文档
│   │
│   ├── pytest_api_mock/           # 【五层数据工厂模式】复杂场景测试
│   │   ├── api_manager/           # L1: 接口层
│   │   ├── data_factory/          # L2-L4: 数据工厂
│   │   │   ├── builders/          # L2: 构造器层
│   │   │   ├── entities/          # L3: 实体层
│   │   │   └── scenarios/         # L4: 场景层
│   │   ├── test_cases/            # L5: 用例层
│   │   ├── fixtures/              # 分层 fixtures
│   │   └── README.md              # 项目文档
│   │
│   └── project_config.py          # 项目配置文件
│
├── core/                          # 核心框架
│   ├── base/                      # 基础类
│   ├── enums/                     # 枚举类型
│   ├── exceptions/                # 异常处理
│   └── models/                    # 数据模型
│
├── service/                       # 服务层
├── settings/                      # 全局配置
├── tools/                         # 工具类
└── README.md                      # 本文档
```

---

## 三种模式详细对比

### 1. api_mock - 抽象页面对象模式

**适用场景**：
- 快速上手 API 自动化测试
- 团队熟悉传统页面对象模式
- 需要简洁直观的测试代码

**核心特点**：
- **分层清晰**：Test Cases → Abstract → API Manager → HTTP Client
- **业务封装**：Abstract 层封装业务操作，测试用例简洁
- **多环境支持**：dev/test/pre/prod 环境一键切换
- **易于维护**：业务逻辑变化只需修改 Abstract 层

**示例代码**：
```python
# abstract/auth/auth.py
class AuthAbstract:
    def login(self, username: str, password: str) -> dict:
        result = self.api.auth.api_login({
            "username": username,
            "password": password
        })
        return result["data"]

# test_cases/test_auth/test_auth.py
class TestLogin:
    def test_login_success(self):
        auth = AuthAbstract()
        result = auth.login("testuser", "password123")
        assert result["token"] is not None
```

---

### 2. bdd_api_mock - BDD + pytest-factoryboy

**适用场景**：
- 业务人员参与测试用例编写
- 需要中文描述的测试场景
- 数据库直连准备测试数据

**核心特点**：
- **Gherkin 语法**：中文编写测试场景，业务可读可写
- **pytest-factoryboy**：自动注册 fixtures，简化数据创建
- **数据库直连**：SQLAlchemy ORM 直接操作数据库
- **自动清理**：Repository 模式自动清理测试数据
- **占位符变量**：`${entity.id}` 语法实现步骤间数据传递

**示例代码**：
```gherkin
# features/auth/auth.feature
# language: zh-CN
功能: 用户认证
  场景: 用户正常登录
    假如 存在"用户"
    当 POST "/auth/login":
      """
      {"username": "${user.username}", "password": "password123"}
      """
    那么 响应状态码应该为 200
```

```python
# factories/specs/user/user_spec.py
@register
class UserSpec(BaseFactory):
    class Meta:
        model = UserEntity
    
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    role = "user"
```

---

### 3. pytest_api_mock - 五层数据工厂模式

**适用场景**：
- 复杂的数据依赖场景（A→B→C→D 链式依赖）
- 需要强类型数据校验
- 状态机驱动的业务流程

**核心特点**：
- **五层架构**：L5→L4→L3→L2→L1 分层设计
- **Pydantic 实体**：L3 使用 Pydantic 定义数据模型
- **数据流向**：`to_api_payload()` 是唯一数据序列化方法
- **依赖自动解决**：A→B→C→D 链式依赖自动构造
- **状态机**：实体状态流转管理
- **血缘追踪**：数据血缘关系追踪

**示例代码**：
```python
# data_factory/entities/order_entity.py
class OrderEntity(BaseModel):
    order_id: str = ""              # 响应字段
    product_id: int = Field(gt=0)  # 请求字段
    
    def to_api_payload(self) -> Dict[str, Any]:
        """唯一数据序列化方法"""
        return {"product_id": self.product_id}

# data_factory/builders/order_builder.py
class OrderBuilder:
    def create_order(self, entity: OrderEntity) -> OrderEntity:
        payload = entity.to_api_payload()  # L3 提供
        result = pytest_api_mock.order.create_order(payload)
        entity.order_id = result["data"]["order_id"]  # 更新响应字段
        return entity

# test_cases/test_order.py
class TestCreateOrder:
    def test_create_order_success(self, order_builder):
        order = OrderEntity.with_product(product_id=1001, quantity=2)
        result = order_builder.create_order(order)
        assert result.order_id  # 后端生成的 ID
```

---

## 快速开始

### 环境准备

确保已安装 Python 3.8+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 选择测试项目

根据测试需求选择合适的项目：

| 需求 | 推荐项目 | 启动命令 |
|------|---------|---------|
| 快速上手、传统模式 | api_mock | `pytest auto_tests/api_mock/` |
| 业务人员参与、中文场景 | bdd_api_mock | `pytest auto_tests/bdd_api_mock/` |
| 复杂依赖、强类型要求 | pytest_api_mock | `pytest auto_tests/pytest_api_mock/` |

### 运行测试示例

```bash
# 1. 抽象页面对象模式
pytest auto_tests/api_mock/test_cases/test_auth/ -v

# 2. BDD 模式
pytest auto_tests/bdd_api_mock/features/auth/ -v

# 3. 五层数据工厂模式
pytest auto_tests/pytest_api_mock/test_cases/test_order.py -v

# 生成 Allure 报告
pytest auto_tests/api_mock/ --alluredir=reports/api_mock/allure
allure serve reports/api_mock/allure
```

---

## 三种模式选型指南

### 选择 api_mock（抽象页面对象模式）如果：

- ✅ 团队熟悉传统页面对象模式
- ✅ 需要快速上手，简洁直观
- ✅ 测试场景相对简单，数据依赖不复杂
- ✅ 希望业务逻辑封装在 Abstract 层

### 选择 bdd_api_mock（BDD 模式）如果：

- ✅ 业务人员需要参与测试用例编写
- ✅ 需要中文描述的测试场景
- ✅ 需要数据库直连准备测试数据
- ✅ 喜欢 Gherkin 语法的 Given/When/Then

### 选择 pytest_api_mock（五层数据工厂模式）如果：

- ✅ 复杂的数据依赖场景（A→B→C→D）
- ✅ 需要强类型数据校验（Pydantic）
- ✅ 需要状态机管理业务流程
- ✅ 需要血缘追踪数据关系
- ✅ 追求极致的可维护性和扩展性

---

## 核心特性

- ✅ **多种架构模式**：三种不同的 API 测试架构，满足不同场景需求
- 📊 **数据管理**：支持 SQLite、Excel、飞书文档三种数据源（可选）
- 👥 **团队协作**：基于飞书文档的在线协同编辑（可选）
- 🔧 **高度可定制**：手动编写测试用例，灵活适应复杂场景
- 📝 **智能通知**：测试结果自动通知相关人员
- 🔄 **动态环境管理**：支持多环境切换，灵活配置测试环境
- 📈 **详细测试报告**：集成 Allure 测试报告，可视化展示结果

---

## 测试报告

项目集成了 Allure 测试报告框架，提供详细的测试执行信息：

- 执行结果统计
- 失败用例详情
- 执行时间分析
- 图片和日志附件

生成报告命令：

```bash
allure generate ./report/tmp -o ./report/html --clean
allure serve ./report/tmp
```

---

## 贡献指南

欢迎任何形式的贡献！

### 提交 Issue

如果您发现了 bug 或者有功能建议，请提交 issue。

### 提交 Pull Request

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 社区支持

#### 加作者微信，进芒果自动化测试群(记得备注：mango_pytest。否则可能会不通过哦)

![img_8.png](img_8.png)

---

## 许可证

### 支持

- 运用在自己公司来完成自动化任务
- 学习、交流测试平台

### 不支持

- 收费教学、二次销售、等盈利活动

### 二次开发注意项

- 请遵守 AGPL-3.0 协议，不支持修改和删除该协议
- 不支持修改包含作者署名版本的内容
- 不支持修改测试平台名称
- 不支持修改和删除 README 中的作者联系方式
- 不支持修改前端项目和执行器项目中的帮助文档跳转操作
