# Fixtures — 浏览器与业务对象装配

主要 Fixture：

| Fixture | 作用域 | 职责 |
|---|---|---|
| `web_runtime` | session | 通过 `sync_web_runtime_session` 管理 `SyncWebRuntime` |
| `base_data` | function | 创建独立 Context/Page，绑定 `BaseData` 并采集产物 |
| `bdd_ui_repositories` | function | 管理隔离 Test Run 与自动清理 |
| `bdd_ui_data_factory` | function | 装配 BDD UI 数据工厂 |
| `order_flow/claim_flow/review_flow` | function | 为公共产品 Flow 注入 Page Object 和项目配置 |

触摸能力用例通过 `request_needs_touch` 临时切换设备，结束后自动恢复。项目 Fixture 不直接创建 Playwright Browser，也不使用旧 `DriverObject` 或 `BaseDataDrives`。
