# Mango Mock API Service

这是一个用于API自动化测试练习的模拟后端服务，基于FastAPI构建。

## 功能特性

- 提供20个常用API接口
- 包含用户认证、增删改查、文件上传等功能
- 支持Docker部署
- 无外部数据库依赖（内存存储）

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

### 认证相关

#### 1. `POST /auth/login` - 用户登录
- **请求头**: `Content-Type: application/json`
- **请求体**: 
  ```json
  {
    "username": "testuser",
    "password": "482c811da5d5b4bc6d497ffa98491e38"  // password123的MD5值
  }
  ```
- **说明**: 密码需要使用MD5加密后传递，后端会对接收到的MD5值与存储的MD5值进行比较
- **响应示例**:
- **请求头**: `Content-Type: application/json`
- **请求体**: 
  ```json
  {
    "username": "testuser",
    "password": "482c811da5d5b4bc6d497ffa98491e38"  // password123的MD5值
  }
  ```
- **说明**: 密码需要使用MD5加密后传递，后端会对接收到的MD5值与存储的MD5值进行比较
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
    "id": 3,
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "newpassword123"
  }
  ```
- **说明**: 注册成功后需要重新登录获取token
- **响应示例**:
- **请求头**: `Content-Type: application/json`
- **请求体**: 
  ```json
  {
    "id": 3,
    "username": "newuser",
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "newpassword123"
  }
  ```
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

### 用户管理

#### 3. `GET /users` - 获取所有用户
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
- **查询参数**: 无
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

#### 4. `GET /users?id={user_id}` - 根据ID获取用户
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
- **查询参数**: `id` - 用户ID
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

#### 5. `PUT /users?id={user_id}` - 更新用户信息
- **请求头**: `Content-Type: application/json`, `X-Token: {登录接口返回的token}`
- **查询参数**: `id` - 用户ID
- **请求体**: 
  ```json
  {
    "id": 1,
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

#### 6. `DELETE /users?id={user_id}` - 删除用户
- **请求头**: `X-Token: {登录接口返回的token}`
- **查询参数**: `id` - 用户ID
- **请求体**: 无
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "删除成功"
  }
  ```

### 产品管理

#### 7. `POST /products` - 创建产品
- **请求头**: `Content-Type: application/json`, `X-Token: {登录接口返回的token}`
- **请求体**: 
  ```json
  {
    "id": 4,
    "name": "New Product",
    "price": 99.99,
    "description": "A new product description"
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
      "description": "A new product description"
    }
  }
  ```

#### 8. `GET /products` - 获取所有产品
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
- **查询参数**: 无
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
        "description": "Latest Apple smartphone"
      }
    ]
  }
  ```

#### 9. `GET /products?id={product_id}` - 根据ID获取产品
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
- **查询参数**: `id` - 产品ID
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "获取成功",
    "data": {
      "id": 1,
      "name": "iPhone 15",
      "price": 999.99,
      "description": "Latest Apple smartphone"
    }
  }
  ```

#### 10. `PUT /products?id={product_id}` - 更新产品信息
- **请求头**: `Content-Type: application/json`, `X-Token: {登录接口返回的token}`
- **查询参数**: `id` - 产品ID
- **请求体**: 
  ```json
  {
    "id": 1,
    "name": "Updated iPhone 15",
    "price": 1099.99,
    "description": "Updated Apple smartphone"
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
      "description": "Updated Apple smartphone"
    }
  }
  ```

#### 11. `DELETE /products?id={product_id}` - 删除产品
- **请求头**: `X-Token: {登录接口返回的token}`
- **查询参数**: `id` - 产品ID
- **请求体**: 无
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "删除成功"
  }
  ```

### 订单管理

#### 12. `POST /orders` - 创建订单
- **请求头**: `Content-Type: application/json`, `X-Token: {登录接口返回的token}`
- **请求体**: 
  ```json
  {
    "id": 3,
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
      "user_id": 1
    }
  }
  ```

#### 13. `GET /orders` - 获取所有订单
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
- **查询参数**: 无
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
        "user_id": 1
      }
    ]
  }
  ```

#### 14. `GET /orders/{order_id}` - 根据ID获取订单
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
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
      "user_id": 1
    }
  }
  ```

#### 15. `PUT /orders?id={order_id}` - 更新订单信息
- **请求头**: `Content-Type: application/json`, `X-Token: {登录接口返回的token}`
- **查询参数**: `id` - 订单ID
- **请求体**: 
  ```json
  {
    "id": 1,
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
      "user_id": 1
    }
  }
  ```

#### 16. `DELETE /orders?id={order_id}` - 删除订单
- **请求头**: `X-Token: {登录接口返回的token}`
- **查询参数**: `id` - 订单ID
- **请求体**: 无
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "删除成功"
  }
  ```

### 其他功能

#### 17. `POST /upload` - 文件上传
- **请求头**: `Content-Type: multipart/form-data`, `X-Token: {登录接口返回的token}`
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

#### 18. `POST /api/data` - 提交数据
- **请求头**: `Content-Type: application/x-www-form-urlencoded`, `X-Token: {登录接口返回的token}`
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

#### 19. `GET /health` - 健康检查
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
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

#### 20. `GET /info` - 获取服务器信息
- **请求头**: `X-Token: {登录接口返回的token}`
- **请求体**: 无
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

## 快速开始

### 使用Docker运行

```bash
# 构建镜像
docker build -t mango-mock .

# 运行容器
docker run -p 8003:8003 mango-mock
```

服务将在 http://localhost:8003 上运行。

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8003
服务将在 http://localhost:8003 上运行。

## API文档

启动服务后，可以通过以下地址访问自动生成的API文档：

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## 测试账号

- 用户名: testuser
- 密码: password123

## 许可证

MIT