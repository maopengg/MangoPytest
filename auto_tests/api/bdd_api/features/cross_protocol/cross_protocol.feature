# language: zh-CN
功能: Mango Mock 跨协议业务一致性

  背景:
    假如 已创建跨协议隔离测试运行
    并且 已登录员工、部门经理、财务经理和总经理

  场景: FTAPI-0120 WebSocket 驱动单节点报销审批
    假如 使用 HTTP 工厂创建大额报销
    当 部门经理通过 WebSocket 审批报销
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "finance_pending"
    并且 跨协议结果保持一致

  场景: FTAPI-0133 MCP 按角色完成报销审批
    假如 使用 MCP 工厂创建大额报销
    当 按角色顺序通过 MCP 完成全部审批
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "approved"
    并且 跨协议结果保持一致

  场景: FTAPI-0154 gRPC 完成报销审批
    假如 使用 gRPC 工厂创建大额报销
    当 按角色顺序通过 gRPC 完成全部审批
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "approved"
    并且 跨协议结果保持一致

  场景: FTAPI-0158 HTTP 创建并由 WebSocket 完成审批
    假如 使用 HTTP 工厂创建大额报销
    当 按角色顺序通过 WebSocket 完成全部审批
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "approved"
    并且 跨协议结果保持一致

  场景: FTAPI-0159 MCP 创建并由 gRPC 完成审批
    假如 使用 MCP 工厂创建大额报销
    当 通过 gRPC 完成 MCP 创建报销的全部审批
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "approved"
    并且 跨协议结果保持一致

  场景: FTAPI-0160 HTTP 启动审查并通过 SSE 观察进度
    假如 使用 HTTP 工厂启动合同审查
    当 通过 SSE 观察合同审查直至完成
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终审查状态为 "completed"
    并且 跨协议结果保持一致

  场景: FTAPI-0161 gRPC 启动审查并通过 MCP 取消
    假如 使用 gRPC 工厂启动合同审查
    当 通过 MCP 取消 gRPC 创建的合同审查
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终审查状态为 "cancelled"
    并且 跨协议结果保持一致

  场景: FTAPI-0162 SSE 与 WebSocket 读取同一业务事件
    假如 使用 HTTP 工厂创建大额报销
    当 分别通过 SSE 和 WebSocket 读取同一审批事件
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "dept_pending"
    并且 跨协议结果保持一致

  场景: FTAPI-0163 WebSocket 断线事件重放
    假如 使用 HTTP 工厂创建大额报销
    当 WebSocket 断线期间通过 HTTP 产生事件后按游标重连
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "finance_pending"
    并且 跨协议结果保持一致

  场景: FTAPI-0164 SSE 断线后续传 MCP 事件
    假如 使用 HTTP 工厂创建大额报销
    当 SSE 断线期间通过 MCP 推进审批后按 Last-Event-ID 重连
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "finance_pending"
    并且 跨协议结果保持一致

  场景: FTAPI-0165 两个 Test Run 的跨协议数据隔离
    假如 两个 Test Run 使用相同业务标识创建报销
    当 分别跨协议验证两个 Test Run 的数据隔离
    那么 通过 HTTP 查询最终业务状态
    并且 最终 HTTP 状态码为 200
    并且 最终业务 code 为 0
    并且 最终报销状态为 "dept_pending"
    并且 跨协议结果保持一致
