# Data Factory — BDD API 测试数据

`data_factory/entities/factories/specs` 保存 BDD 模式自己的强类型数据定义和构造规则。步骤层通过 Factory 创建前置数据，禁止在 Feature 或测试绑定文件中直接调用 API。

数据工厂调用领域 Repository；Repository 再复用公共 Mango Mock 协议客户端。测试数据位于隔离 Test Run，结束后统一清理。
