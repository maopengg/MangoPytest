# Mango Mock API Service

这是一个用于API自动化测试练习的模拟后端服务，基于FastAPI构建。

## 功能特性

- 提供30+个常用API接口
- 包含用户认证、增删改查、文件上传、审批流程等功能
- 支持Docker部署
- 支持MySQL数据库存储
- 完整的报销审批工作流（D→C→B→A四级审批）

## 接口详细说明

### 访问令牌 (Token)

除登录接口外，所有接口都需要在请求头中包含有效的访问令牌。

1. 首先调用登录接口获取token:
   ```bash
   curl -X POST http://localhost:8003/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "482c811da5d5b4bc6d497ffa98491e38"}'
   ```
2. 从响应中提取token值:
   ```json
   {
     "code": 200,
     "message": "登录成功",
     "data": {
       "user_id": 1,
       "username": "testuser",
       "token": "mock_token_xxxxxx"
     }
   }
   ```
3. 在后续请求中添加X-Token头:
   ```bash
   curl -X GET http://localhost:8003/users \
        -H "X-Token: mock_token_xxxxxx"
   ```

如果未提供有效的token，接口将返回401 Unauthorized错误。

***

### 认证相关

#### 1. `POST /auth/login` - 用户登录

- **请求头**: `Content-Type: application/json`
- **请求体**: 不允许使用这个账号进行修改，删除等操作，这是固定给登陆用户使用的账号
  ```json
  {
    "username": "testuser",
    "password": "482c811da5d5b4bc6d497ffa98491e38"
  }
  ```
- **说明**: 密码需要使用MD5加密后传递
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "user_id": 1,
      "username": "testuser",
      "token": "mock_token_xxxxxx"
    }
  }
  ```

#### 2. `POST /auth/register` - 用户注册

- **请求头**: `Content-Type: application/json`
- **请求体**:
  ```json
  {
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "newpassword123"
  }
  ```
- **说明**: 注册成功后需要重新登录获取token
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "注册成功",
    "data": {
      "id": 3,
      "username": "newuser",
      "email": "newuser@example.com",
      "full_name": "New User"
    }
  }
  ```

***

### 用户管理

#### 3. `GET /users` - 获取所有用户

- **请求头**: `X-Token: {token}`
- **请求体**: 无
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User"
      }
    ]
  }
  ```

#### 4. `GET /users/{user_id}` - 根据ID获取用户

- **请求头**: `X-Token: {token}`
- **路径参数**: `user_id` - 用户ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "full_name": "Test User"
    }
  }
  ```

#### 5. `PUT /users/{user_id}` - 更新用户信息

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **路径参数**: `user_id` - 用户ID
- **请求体**:
  ```json
  {
    "username": "updateduser",
    "email": "updated@example.com",
    "full_name": "Updated User"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "id": 1,
      "username": "updateduser",
      "email": "updated@example.com",
      "full_name": "Updated User"
    }
  }
  ```

#### 6. `DELETE /users/{user_id}` - 删除用户

- **请求头**: `X-Token: {token}`
- **路径参数**: `user_id` - 用户ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "删除成功"
  }
  ```

***

### 产品管理

#### 7. `POST /products` - 创建产品

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **请求体**:
  ```json
  {
    "name": "New Product",
    "price": 99.99,
    "description": "A new product description",
    "stock": 100
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "id": 4,
      "name": "New Product",
      "price": 99.99,
      "description": "A new product description",
      "stock": 100
    }
  }
  ```

#### 8. `GET /products` - 获取所有产品

- **请求头**: `X-Token: {token}`
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "name": "iPhone 15",
        "price": 999.99,
        "description": "Latest Apple smartphone",
        "stock": 100
      }
    ]
  }
  ```

#### 9. `PUT /products/{product_id}` - 更新产品信息

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **路径参数**: `product_id` - 产品ID
- **请求体**:
  ```json
  {
    "name": "Updated iPhone 15",
    "price": 1099.99,
    "description": "Updated Apple smartphone",
    "stock": 50
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "id": 1,
      "name": "Updated iPhone 15",
      "price": 1099.99,
      "description": "Updated Apple smartphone",
      "stock": 50
    }
  }
  ```

#### 10. `DELETE /products/{product_id}` - 删除产品

- **请求头**: `X-Token: {token}`
- **路径参数**: `product_id` - 产品ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "删除成功"
  }
  ```

***

### 订单管理

#### 11. `POST /orders` - 创建订单

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **请求体**:
  ```json
  {
    "product_id": 1,
    "quantity": 2,
    "user_id": 1
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "创建成功",
    "data": {
      "id": 3,
      "product_id": 1,
      "quantity": 2,
      "user_id": 1,
      "total_price": 1999.98,
      "status": "pending"
    }
  }
  ```

#### 12. `GET /orders` - 获取所有订单

- **请求头**: `X-Token: {token}`
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "product_id": 1,
        "quantity": 2,
        "user_id": 1,
        "total_price": 1999.98,
        "status": "completed"
      }
    ]
  }
  ```

#### 13. `GET /orders/{order_id}` - 根据ID获取订单

- **请求头**: `X-Token: {token}`
- **路径参数**: `order_id` - 订单ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "user_id": 1,
      "total_price": 1999.98,
      "status": "completed"
    }
  }
  ```

#### 14. `PUT /orders/{order_id}` - 更新订单信息

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **路径参数**: `order_id` - 订单ID
- **请求体**:
  ```json
  {
    "product_id": 2,
    "quantity": 3,
    "user_id": 1
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "id": 1,
      "product_id": 2,
      "quantity": 3,
      "user_id": 1,
      "total_price": 2999.97,
      "status": "pending"
    }
  }
  ```

#### 15. `DELETE /orders/{order_id}` - 删除订单

- **请求头**: `X-Token: {token}`
- **路径参数**: `order_id` - 订单ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "删除成功"
  }
  ```

***

### 报销申请管理 (D级模块)

#### 16. `POST /reimbursements` - 创建报销申请

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **请求体**:
  ```json
  {
    "user_id": 1,
    "amount": 1000.00,
    "reason": "差旅报销",
    "category": "travel",
    "attachments": ["file1.jpg", "file2.pdf"]
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "报销申请创建成功",
    "data": {
      "id": 1,
      "reimb_no": "RMB20260402094448d9c4",
      "user_id": 1,
      "amount": 1000.00,
      "reason": "差旅报销",
      "category": "travel",
      "status": "pending",
      "current_step": 1,
      "submitted_at": "2026-04-02T09:44:49",
      "created_at": "2026-04-02T09:44:49",
      "updated_at": "2026-04-02T09:44:49"
    }
  }
  ```

#### 17. `GET /reimbursements` - 获取报销申请列表

- **请求头**: `X-Token: {token}`
- **查询参数**:
  - `status` (可选): 状态筛选 (pending, dept\_approved, finance\_approved, ceo\_approved, rejected)
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "reimb_no": "RMB20260402094448d9c4",
        "user_id": 1,
        "amount": 1000.00,
        "reason": "差旅报销",
        "status": "pending",
        "current_step": 1
      }
    ]
  }
  ```

#### 18. `PUT /reimbursements/{reimbursement_id}` - 更新报销申请

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **路径参数**: `reimbursement_id` - 报销申请ID
- **请求体**:
  ```json
  {
    "amount": 1500.00,
    "reason": "更新后的报销原因",
    "category": "office"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "更新成功",
    "data": {
      "id": 1,
      "amount": 1500.00,
      "reason": "更新后的报销原因",
      "category": "office"
    }
  }
  ```

#### 19. `DELETE /reimbursements/{reimbursement_id}` - 删除报销申请

- **请求头**: `X-Token: {token}`
- **路径参数**: `reimbursement_id` - 报销申请ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "删除成功"
  }
  ```

***

### 部门审批管理 (C级模块)

#### 20. `POST /dept-approvals` - 创建部门审批

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **请求体**:
  ```json
  {
    "reimbursement_id": 1,
    "approver_id": 2,
    "status": "approved",
    "comment": "部门审批通过"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "部门审批创建成功",
    "data": {
      "id": 1,
      "reimbursement_id": 1,
      "approver_id": 2,
      "status": "approved",
      "comment": "部门审批通过",
      "approved_at": "2026-04-02T10:00:00"
    }
  }
  ```

#### 21. `GET /dept-approvals` - 获取部门审批列表

- **请求头**: `X-Token: {token}`
- **查询参数**:
  - `reimbursement_id` (可选): 按报销申请ID筛选
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "reimbursement_id": 1,
        "approver_id": 2,
        "status": "approved",
        "comment": "部门审批通过"
      }
    ]
  }
  ```

***

### 财务审批管理 (B级模块)

#### 22. `POST /finance-approvals` - 创建财务审批

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **请求体**:
  ```json
  {
    "reimbursement_id": 1,
    "dept_approval_id": 1,
    "approver_id": 3,
    "status": "approved",
    "comment": "财务审批通过"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "财务审批创建成功",
    "data": {
      "id": 1,
      "reimbursement_id": 1,
      "dept_approval_id": 1,
      "approver_id": 3,
      "status": "approved",
      "comment": "财务审批通过",
      "approved_at": "2026-04-02T10:30:00"
    }
  }
  ```

#### 23. `GET /finance-approvals` - 获取财务审批列表

- **请求头**: `X-Token: {token}`
- **查询参数**:
  - `reimbursement_id` (可选): 按报销申请ID筛选
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "reimbursement_id": 1,
        "dept_approval_id": 1,
        "approver_id": 3,
        "status": "approved",
        "comment": "财务审批通过"
      }
    ]
  }
  ```

***

### 总经理审批管理 (A级模块)

#### 24. `POST /ceo-approvals` - 创建总经理审批

- **请求头**: `Content-Type: application/json`, `X-Token: {token}`
- **请求体**:
  ```json
  {
    "reimbursement_id": 1,
    "finance_approval_id": 1,
    "approver_id": 4,
    "status": "approved",
    "comment": "总经理审批通过"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "总经理审批创建成功",
    "data": {
      "id": 1,
      "reimbursement_id": 1,
      "finance_approval_id": 1,
      "approver_id": 4,
      "status": "approved",
      "comment": "总经理审批通过",
      "approved_at": "2026-04-02T11:00:00"
    }
  }
  ```

#### 25. `GET /ceo-approvals` - 获取总经理审批列表

- **请求头**: `X-Token: {token}`
- **查询参数**:
  - `reimbursement_id` (可选): 按报销申请ID筛选
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": [
      {
        "id": 1,
        "reimbursement_id": 1,
        "finance_approval_id": 1,
        "approver_id": 4,
        "status": "approved",
        "comment": "总经理审批通过"
      }
    ]
  }
  ```

***

### 审批工作流

#### 26. `GET /workflow/{reimbursement_id}` - 获取完整审批流程

- **请求头**: `X-Token: {token}`
- **路径参数**: `reimbursement_id` - 报销申请ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "reimbursement": {
        "id": 1,
        "reimb_no": "RMB20260402094448d9c4",
        "amount": 1000.00,
        "status": "fully_approved"
      },
      "dept_approval": {
        "id": 1,
        "approver_id": 2,
        "status": "approved"
      },
      "finance_approval": {
        "id": 1,
        "approver_id": 3,
        "status": "approved"
      },
      "ceo_approval": {
        "id": 1,
        "approver_id": 4,
        "status": "approved"
      }
    }
  }
  ```

***

### 其他功能

#### 27. `POST /upload` - 文件上传

- **请求头**: `Content-Type: multipart/form-data`, `X-Token: {token}`
- **请求体**: 表单数据，包含文件字段 `file`
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "上传成功",
    "data": {
      "filename": "example.txt",
      "content_type": "text/plain",
      "size": 1024,
      "file_id": "uuid-string"
    }
  }
  ```

#### 28. `POST /api/data` - 提交数据

- **请求头**: `Content-Type: application/x-www-form-urlencoded`, `X-Token: {token}`
- **请求体**: 表单数据，包含字段 `name` 和 `value`
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "数据提交成功",
    "data": {
      "name": "example",
      "value": 123,
      "timestamp": "2023-01-01T00:00:00"
    }
  }
  ```

#### 29. `GET /health` - 健康检查

- **请求头**: `X-Token: {token}`
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "服务正常运行",
    "data": {
      "status": "healthy",
      "timestamp": "2023-01-01T00:00:00"
    }
  }
  ```

#### 30. `GET /info` - 获取服务器信息

- **请求头**: `X-Token: {token}`
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "app_name": "Mock API Service",
      "version": "1.0.0",
      "framework": "FastAPI",
      "python_version": "3.10"
    }
  }
  ```

#### 31. `GET /startup` - 初始化数据

- **请求头**: 无
- **说明**: 初始化测试数据（用户、产品等）
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "数据初始化成功",
    "data": {
      "users_count": 5,
      "products_count": 3,
      "orders_count": 2
    }
  }
  ```

***

## 快速开始

### 使用Docker运行

```bash
# 构建镜像
docker build -t mango-mock .

# 运行容器
docker run -p 8003:8003 mango-mock
```

服务将在 <http://localhost:8003> 上运行。

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn service.mock_api:app --host 0.0.0.0 --port 8003
```

服务将在 <http://localhost:8003> 上运行。

## API文档

启动服务后，可以通过以下地址访问自动生成的API文档：

- Swagger UI: <http://localhost:8003/docs>
- ReDoc: <http://localhost:8003/redoc>

## 测试账号

- 用户名: testuser
- 密码: password123（MD5: 482c811da5d5b4bc6d497ffa98491e38）

## 审批流程说明

系统实现了完整的四级审批流程（D→C→B→A）：

1. **D级 - 报销申请**: 员工提交报销申请
2. **C级 - 部门审批**: 部门经理审批（需要D级通过）
3. **B级 - 财务审批**: 财务经理审批（需要C级通过）
4. **A级 - 总经理审批**: CEO审批（大额需要，需要B级通过）

状态流转：

```
pending → dept_approved → finance_approved → ceo_approved → fully_approved
   ↓           ↓                ↓                  ↓
rejected    rejected         rejected           rejected
```

## 许可证

MIT License
