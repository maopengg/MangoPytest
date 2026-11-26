# 可选 HTTP Mock 服务

开源和公司仓库维护相同的本地模拟服务。接口开发未完成时可用于联调、数据工厂和自动化验证；不会随测试收集或 Web Console 自动启动。

`mock_api.py` 提供基于 MySQL 的认证、用户、商品、订单及审批等示例接口，`init_tables.sql` 是建表样例，[API 参考](API参考.md) 和 [用例说明](MockAPI测试用例.md) 描述接口行为。这里不包含 UI 页面或 gRPC 服务；完整多协议靶场由独立 `mango-mock` 仓库维护。

## 配置和启动

使用根 `requirements.txt` 安装依赖，数据库驱动由内部 wheel 关联安装。准备独立的测试 MySQL 数据库，核对 `init_tables.sql` 后手工导入；脚本包含 `DROP TABLE`，会重建同名表，不要用于已有业务数据库。

数据库连接使用环境变量，不在源码保存真实密码：

| 变量 | 默认值 |
|---|---|
| `MOCK_MYSQL_HOST` | `127.0.0.1` |
| `MOCK_MYSQL_PORT` | `3306` |
| `MOCK_MYSQL_USER` | `root` |
| `MOCK_MYSQL_PASSWORD` | 空，通过环境变量注入 |
| `MOCK_MYSQL_DATABASE` | `mango_mock` |
| `MOCK_HOST` | `127.0.0.1` |
| `MOCK_PORT` | `8003` |

确认数据库配置后，从仓库根目录显式启动：

```bash
ENV=test .venv/bin/python -m mock.mock_api
```

浏览 `http://127.0.0.1:8003/docs` 查看接口，根路径跳转到文档。使用其他端口时设置 `MOCK_PORT`，或用 `.venv/bin/python -m uvicorn mock.mock_api:app --host 127.0.0.1 --port 8003` 显式指定监听参数。用例的服务地址仍通过对应项目配置的 `BASE_URL` 设置，不自动覆盖业务地址。

服务需连接数据库的接口在首次请求时建立连接；导入模块、访问接口文档不会连接数据库。通用能力保留在此处，产品专属 Mock 按产品归入 `auto_tests/common/<product>/mock/`。
