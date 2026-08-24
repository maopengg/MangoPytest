# BDD UI 模式

`bdd_ui` 使用中文 Gherkin 表达业务场景，浏览器运行时和 Mango Mock 产品实现均复用公共层。

## 当前结构

```text
auto_tests/ui/bdd_ui/
├── features/                 # 业务与能力 Feature
├── test_cases/               # pytest-bdd 场景绑定
├── steps/                    # 领域步骤与断言
├── fixtures/                 # 项目级对象装配
├── data_factory/             # BDD 独立的 Entity/Factory/Spec
├── capabilities/cases/       # BDD Case ID 装配
├── config/                   # 项目环境配置
├── contexts.py               # 强类型场景上下文
└── conftest.py               # 插件与优先级标记注册
```

公共实现分为两层：

- `core/ui/`：浏览器生命周期、元素 Runtime、产物采集。
- `core/sources/`：Excel/飞书元素来源与字段映射。
- `auto_tests/common/mango_mock/`：产品 Page Object、Flow、Repository、能力执行器和能力模型。

## 调用链

```text
Feature → Steps → Fixture 装配 → Flow + Data Factory
        → Mango Mock Page Object / Repository
        → SyncWebRuntime / 公共协议客户端
```

BDD 与纯 pytest UI 可以共享产品实现，但不能共享 Feature、Steps、Fixture 和数据工厂，以便完整演示两种自动化组织方式。
