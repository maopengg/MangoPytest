# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Mock API Service - 使用MySQL存储
# @Time   : 2026-04-01
# @Author : 毛鹏

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List, Dict, Any
import uvicorn
import uuid
from datetime import datetime
import hashlib
from pydantic import BaseModel
from fastapi import Request, UploadFile, File
import pymysql
from contextlib import contextmanager
import json
import time

# MySQL 配置
MYSQL_CONFIG = {
    "host": "43.142.161.61",
    "port": 3306,
    "user": "root",
    "password": "mP123456&",
    "database": "mango_mock",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

app = FastAPI(title="Mock API Service", description="使用MySQL存储的模拟后端服务")

# ========================
# 请求/响应日志中间件
# ========================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求/响应日志中间件
    记录所有请求和响应的详细信息
    """
    start_time = time.time()
    
    # 生成请求ID
    request_id = str(uuid.uuid4())[:8]
    
    # 获取请求信息
    method = request.method
    url = str(request.url)
    client_host = request.client.host if request.client else "unknown"
    
    # 尝试获取请求体
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            body_bytes = await request.body()
            if body_bytes:
                body = body_bytes.decode('utf-8')
                # 重新设置请求体，以便后续处理
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
        except Exception as e:
            body = f"无法读取请求体: {e}"
    
    # 打印请求日志
    print(f"\n{'='*80}")
    print(f"[{request_id}] 🚀 请求: {method} {url}")
    print(f"[{request_id}] 📍 客户端: {client_host}")
    print(f"[{request_id}] 📋 Headers: {dict(request.headers)}")
    if body:
        try:
            # 尝试格式化 JSON
            body_json = json.loads(body)
            # 隐藏敏感信息（密码）
            if isinstance(body_json, dict) and 'password' in body_json:
                body_json['password'] = '***'
            print(f"[{request_id}] 📦 Body: {json.dumps(body_json, ensure_ascii=False, indent=2)}")
        except:
            print(f"[{request_id}] 📦 Body: {body[:500]}")  # 限制长度
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (time.time() - start_time) * 1000
        
        # 打印响应日志
        status_code = response.status_code
        status_icon = "✅" if status_code < 400 else "❌"
        print(f"[{request_id}] {status_icon} 响应: {status_code} ({process_time:.2f}ms)")
        
        # 尝试读取响应体
        try:
            response_body = [section async for section in response.__dict__.get('body_iterator', [])]
            if response_body:
                body_content = b''.join(response_body).decode('utf-8')
                try:
                    body_json = json.loads(body_content)
                    print(f"[{request_id}] 📤 Response: {json.dumps(body_json, ensure_ascii=False, indent=2)[:1000]}")
                except:
                    print(f"[{request_id}] 📤 Response: {body_content[:500]}")
        except Exception as e:
            print(f"[{request_id}] ⚠️ 无法读取响应体: {e}")
        
        print(f"{'='*80}\n")
        
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        print(f"[{request_id}] 💥 异常: {str(e)} ({process_time:.2f}ms)")
        print(f"{'='*80}\n")
        raise

# ========================
# CORS中间件
# ========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# ========================
# 数据库连接管理
# ========================

@contextmanager
def get_db_connection():
    """获取数据库连接上下文管理器"""
    conn = None
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        yield conn
    except Exception as e:
        print(f"数据库连接错误: {e}")
        raise
    finally:
        if conn:
            conn.close()


@contextmanager
def get_db_cursor():
    """获取数据库游标上下文管理器"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()


# ========================
# 模型定义
# ========================

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    full_name: str
    password: str
    role: str = "user"
    status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    description: Optional[str] = None
    stock: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Order(BaseModel):
    id: Optional[int] = None
    product_id: int
    quantity: int
    user_id: int
    total_amount: float = 0.0
    status: str = "pending"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DataModel(BaseModel):
    name: str
    value: str | int


# 审批流模型
class Reimbursement(BaseModel):
    """D级：报销申请"""
    id: Optional[int] = None
    user_id: int
    amount: float
    reason: str
    status: str = "pending"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DeptApproval(BaseModel):
    """C级：部门审批"""
    id: Optional[int] = None
    reimbursement_id: int
    approver_id: int
    status: str
    comment: Optional[str] = None
    created_at: Optional[str] = None


class FinanceApproval(BaseModel):
    """B级：财务审批"""
    id: Optional[int] = None
    reimbursement_id: int
    dept_approval_id: int
    approver_id: int
    status: str
    comment: Optional[str] = None
    created_at: Optional[str] = None


class CEOApproval(BaseModel):
    """A级：总经理审批"""
    id: Optional[int] = None
    reimbursement_id: int
    finance_approval_id: int
    approver_id: int
    status: str
    comment: Optional[str] = None
    created_at: Optional[str] = None


# ========================
# 工具函数
# ========================

def success(data=None, message="成功"):
    return {"code": 200, "message": message, "data": data}


def error(code, message):
    return {"code": code, "message": message, "data": None}


async def verify_token(x_token: str = Header(None)):
    if x_token is None:
        raise HTTPException(status_code=401, detail="未提供token")
    if not x_token.startswith("mock_token_"):
        raise HTTPException(status_code=401, detail="无效的token")
    return x_token


# ========================
# 路由
# ========================

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


# ========================
# 1. 登录
# ========================

@app.post("/auth/login", summary="用户登录")
async def login(user_login: UserLogin):
    if user_login.username.strip() == "" or user_login.password.strip() == "":
        return error(400, "用户名或密码不能为空")
    
    try:
        with get_db_cursor() as cursor:
            # 查询用户
            sql = "SELECT * FROM users WHERE username = %s AND status = 'active'"
            cursor.execute(sql, (user_login.username,))
            user = cursor.fetchone()
            
            if not user:
                return error(401, "用户名或密码错误")
            
            # 验证密码（MD5）
            password_md5 = hashlib.md5(user_login.password.encode()).hexdigest()
            if password_md5 != user['password']:
                return error(402, "用户名或密码错误")
            
            # 更新最后登录时间
            sql = "UPDATE users SET updated_at = NOW() WHERE id = %s"
            cursor.execute(sql, (user['id'],))
            
            return success(
                {
                    "user_id": user['id'],
                    "username": user['username'],
                    "role": user['role'],
                    "token": f"mock_token_{uuid.uuid4()}",
                },
                "登录成功",
            )
    except Exception as e:
        return error(500, f"登录失败: {str(e)}")


# ========================
# 2. 注册
# ========================

@app.post("/auth/register", summary="用户注册")
async def register(user: UserCreate):
    if user.username.strip() == "" or user.password.strip() == "":
        return error(400, "用户名或密码不能为空")
    
    try:
        with get_db_cursor() as cursor:
            # 检查用户名是否已存在
            sql = "SELECT id FROM users WHERE username = %s"
            cursor.execute(sql, (user.username,))
            if cursor.fetchone():
                return error(400, "用户名已存在")
            
            # 创建用户
            password_md5 = hashlib.md5(user.password.encode()).hexdigest()
            sql = """
                INSERT INTO users (username, email, full_name, password, role, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, 'active', NOW(), NOW())
            """
            cursor.execute(sql, (user.username, user.email, user.full_name, password_md5, user.role))
            user_id = cursor.lastrowid
            
            # 查询新创建的用户
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            new_user = cursor.fetchone()
            
            return success(
                {
                    "id": new_user['id'],
                    "username": new_user['username'],
                    "email": new_user['email'],
                    "full_name": new_user['full_name'],
                    "role": new_user['role'],
                },
                "注册成功"
            )
    except Exception as e:
        return error(500, f"注册失败: {str(e)}")


# ========================
# 3. 用户管理
# ========================

@app.get("/users", summary="获取用户列表")
async def get_users(id: Optional[int] = None, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            if id is not None:
                sql = "SELECT * FROM users WHERE id = %s"
                cursor.execute(sql, (id,))
                user = cursor.fetchone()
                if user:
                    # 隐藏密码
                    user.pop('password', None)
                    return success(user, "获取成功")
                return error(404, "用户不存在")
            
            sql = "SELECT id, username, email, full_name, role, status, created_at, updated_at FROM users WHERE status = 'active'"
            cursor.execute(sql)
            users = cursor.fetchall()
            return success(users, "获取成功")
    except Exception as e:
        return error(500, f"获取用户失败: {str(e)}")


@app.put("/users/{user_id}", summary="更新用户")
async def update_user(user_id: int, user: User, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            # 检查用户是否存在
            sql = "SELECT id FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            if not cursor.fetchone():
                return error(404, "用户不存在")
            
            # 更新用户
            sql = """
                UPDATE users 
                SET username = %s, email = %s, full_name = %s, role = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(sql, (user.username, user.email, user.full_name, user.role, user_id))
            
            # 查询更新后的用户
            sql = "SELECT id, username, email, full_name, role, status, created_at, updated_at FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            updated_user = cursor.fetchone()
            
            return success(updated_user, "更新成功")
    except Exception as e:
        return error(500, f"更新用户失败: {str(e)}")


@app.delete("/users/{user_id}", summary="删除用户")
async def delete_user(user_id: int, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            # 检查用户是否存在
            sql = "SELECT id FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            if not cursor.fetchone():
                return error(404, "用户不存在")
            
            # 软删除用户
            sql = "UPDATE users SET status = 'deleted', updated_at = NOW() WHERE id = %s"
            cursor.execute(sql, (user_id,))
            
            return success(None, "删除成功")
    except Exception as e:
        return error(500, f"删除用户失败: {str(e)}")


# ========================
# 产品管理
# ========================

@app.post("/products", summary="创建产品")
async def create_product(product: Product, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            sql = """
                INSERT INTO products (name, price, description, stock, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(sql, (product.name, product.price, product.description, product.stock))
            product_id = cursor.lastrowid
            
            sql = "SELECT * FROM products WHERE id = %s"
            cursor.execute(sql, (product_id,))
            new_product = cursor.fetchone()
            
            return success(new_product, "创建成功")
    except Exception as e:
        return error(500, f"创建产品失败: {str(e)}")


@app.get("/products", summary="获取产品列表")
async def get_products(id: Optional[int] = None, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            if id is not None:
                sql = "SELECT * FROM products WHERE id = %s"
                cursor.execute(sql, (id,))
                product = cursor.fetchone()
                if product:
                    return success(product, "获取成功")
                return error(404, "产品不存在")
            
            sql = "SELECT * FROM products ORDER BY id DESC"
            cursor.execute(sql)
            products = cursor.fetchall()
            return success(products, "获取成功")
    except Exception as e:
        return error(500, f"获取产品失败: {str(e)}")


@app.put("/products/{product_id}", summary="更新产品")
async def update_product(product_id: int, product: Product, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            sql = "SELECT id FROM products WHERE id = %s"
            cursor.execute(sql, (product_id,))
            if not cursor.fetchone():
                return error(404, "产品不存在")
            
            sql = """
                UPDATE products 
                SET name = %s, price = %s, description = %s, stock = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(sql, (product.name, product.price, product.description, product.stock, product_id))
            
            sql = "SELECT * FROM products WHERE id = %s"
            cursor.execute(sql, (product_id,))
            updated_product = cursor.fetchone()
            
            return success(updated_product, "更新成功")
    except Exception as e:
        return error(500, f"更新产品失败: {str(e)}")


@app.delete("/products/{product_id}", summary="删除产品")
async def delete_product(product_id: int, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            sql = "SELECT id FROM products WHERE id = %s"
            cursor.execute(sql, (product_id,))
            if not cursor.fetchone():
                return error(404, "产品不存在")
            
            sql = "DELETE FROM products WHERE id = %s"
            cursor.execute(sql, (product_id,))
            
            return success(None, "删除成功")
    except Exception as e:
        return error(500, f"删除产品失败: {str(e)}")


# ========================
# 订单管理
# ========================

@app.post("/orders", summary="创建订单")
async def create_order(order: Order, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            # 检查产品是否存在
            sql = "SELECT price, stock FROM products WHERE id = %s"
            cursor.execute(sql, (order.product_id,))
            product = cursor.fetchone()
            if not product:
                return error(404, "产品不存在")
            
            if product['stock'] < order.quantity:
                return error(400, "库存不足")
            
            # 计算订单金额
            total_amount = product['price'] * order.quantity
            
            # 创建订单
            sql = """
                INSERT INTO orders (product_id, quantity, user_id, total_amount, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, 'pending', NOW(), NOW())
            """
            cursor.execute(sql, (order.product_id, order.quantity, order.user_id, total_amount))
            order_id = cursor.lastrowid
            
            # 减少库存
            sql = "UPDATE products SET stock = stock - %s WHERE id = %s"
            cursor.execute(sql, (order.quantity, order.product_id))
            
            sql = "SELECT * FROM orders WHERE id = %s"
            cursor.execute(sql, (order_id,))
            new_order = cursor.fetchone()
            
            return success(new_order, "创建成功")
    except Exception as e:
        return error(500, f"创建订单失败: {str(e)}")


@app.get("/orders", summary="获取订单列表")
async def get_orders(token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            sql = """
                SELECT o.*, p.name as product_name, u.username 
                FROM orders o
                LEFT JOIN products p ON o.product_id = p.id
                LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.id DESC
            """
            cursor.execute(sql)
            orders = cursor.fetchall()
            return success(orders, "获取成功")
    except Exception as e:
        return error(500, f"获取订单失败: {str(e)}")


@app.get("/orders/{order_id}", summary="获取订单详情")
async def get_order(order_id: int, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            sql = """
                SELECT o.*, p.name as product_name, u.username 
                FROM orders o
                LEFT JOIN products p ON o.product_id = p.id
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.id = %s
            """
            cursor.execute(sql, (order_id,))
            order = cursor.fetchone()
            if order:
                return success(order, "获取成功")
            return error(404, "订单不存在")
    except Exception as e:
        return error(500, f"获取订单失败: {str(e)}")


@app.put("/orders/{order_id}", summary="更新订单")
async def update_order(order_id: int, order: Order, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            sql = "SELECT id FROM orders WHERE id = %s"
            cursor.execute(sql, (order_id,))
            if not cursor.fetchone():
                return error(404, "订单不存在")
            
            sql = """
                UPDATE orders 
                SET status = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(sql, (order.status, order_id))
            
            sql = "SELECT * FROM orders WHERE id = %s"
            cursor.execute(sql, (order_id,))
            updated_order = cursor.fetchone()
            
            return success(updated_order, "更新成功")
    except Exception as e:
        return error(500, f"更新订单失败: {str(e)}")


@app.delete("/orders/{order_id}", summary="删除订单")
async def delete_order(order_id: int, token: str = Depends(verify_token)):
    try:
        with get_db_cursor() as cursor:
            sql = "SELECT id FROM orders WHERE id = %s"
            cursor.execute(sql, (order_id,))
            if not cursor.fetchone():
                return error(404, "订单不存在")
            
            sql = "DELETE FROM orders WHERE id = %s"
            cursor.execute(sql, (order_id,))
            
            return success(None, "删除成功")
    except Exception as e:
        return error(500, f"删除订单失败: {str(e)}")


# ========================
# 数据提交
# ========================

@app.post("/api/data", summary="提交数据")
async def submit_data(request: Request, token: str = Depends(verify_token)):
    try:
        # 取 query 参数
        query_params = dict(request.query_params)
        
        # 取 body 参数
        try:
            body = await request.json()
            if not isinstance(body, dict):
                body = {}
        except:
            body = {}
        
        # 合并参数（body 优先生效）
        params = {**query_params, **body}
        
        name = str(params.get("name", "")).strip()
        value = str(params.get("value", "")).strip()
        
        if name == "":
            return error(400, "name不能为空")
        
        if value == "":
            return error(400, "value不能为空")
        
        if not value.isdigit():
            return error(400, "value必须是整数")
        
        # 存储到数据库
        with get_db_cursor() as cursor:
            sql = """
                INSERT INTO data_submissions (name, value, created_at)
                VALUES (%s, %s, NOW())
            """
            cursor.execute(sql, (name, int(value)))
        
        return success(
            {"name": name, "value": int(value), "timestamp": datetime.now().isoformat()},
            "数据提交成功",
        )
    except Exception as e:
        return error(500, f"数据提交失败: {str(e)}")


# ========================
# 上传文件
# ========================

@app.post("/upload", summary="上传文件")
async def upload_file(file: UploadFile = File(...), token: str = Depends(verify_token)):
    try:
        file_content = await file.read()
        file_size = len(file_content)
        file_id = str(uuid.uuid4())
        
        # 存储文件信息到数据库
        with get_db_cursor() as cursor:
            sql = """
                INSERT INTO files (file_id, filename, content_type, size, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (file_id, file.filename, file.content_type, file_size))
        
        return success(
            {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file_size,
                "file_id": file_id,
            },
            "上传成功",
        )
    except Exception as e:
        return error(500, f"文件上传失败: {str(e)}")


# ========================
# 健康检查
# ========================

@app.get("/health", summary="健康检查")
async def health_check(token: str = Depends(verify_token)):
    try:
        # 检查数据库连接
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        
        return success(
            {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            },
            "服务正常运行"
        )
    except Exception as e:
        return error(503, f"服务异常: {str(e)}")


# ========================
# 服务器信息
# ========================

@app.get("/info", summary="服务器信息")
async def server_info(token: str = Depends(verify_token)):
    return success(
        {
            "app_name": "Mock API Service",
            "version": "2.0.0",
            "framework": "FastAPI",
            "python_version": "3.10",
            "database": "MySQL",
        },
        "获取成功",
    )


# ========================
# 审批流模块 - 4级审批
# ========================

@app.post("/reimbursements", summary="创建报销申请")
async def create_reimbursement(reimbursement: Reimbursement, token: str = Depends(verify_token)):
    """D级模块：创建报销申请"""
    if reimbursement.amount <= 0:
        return error(400, "报销金额必须大于0")
    
    if not reimbursement.reason or reimbursement.reason.strip() == "":
        return error(400, "报销原因不能为空")
    
    try:
        with get_db_cursor() as cursor:
            sql = """
                INSERT INTO reimbursements (user_id, amount, reason, status, created_at, updated_at)
                VALUES (%s, %s, %s, 'pending', NOW(), NOW())
            """
            cursor.execute(sql, (reimbursement.user_id, reimbursement.amount, reimbursement.reason))
            reimb_id = cursor.lastrowid
            
            sql = "SELECT * FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (reimb_id,))
            new_reimb = cursor.fetchone()
            
            return success(new_reimb, "报销申请创建成功")
    except Exception as e:
        return error(500, f"创建报销申请失败: {str(e)}")


@app.get("/reimbursements", summary="获取报销申请列表")
async def get_reimbursements(id: Optional[int] = None, token: str = Depends(verify_token)):
    """D级模块：获取报销申请列表"""
    try:
        with get_db_cursor() as cursor:
            if id is not None:
                sql = "SELECT * FROM reimbursements WHERE id = %s"
                cursor.execute(sql, (id,))
                reimb = cursor.fetchone()
                if reimb:
                    return success(reimb, "获取成功")
                return error(404, "报销申请不存在")
            
            sql = """
                SELECT r.*, u.username 
                FROM reimbursements r
                LEFT JOIN users u ON r.user_id = u.id
                ORDER BY r.id DESC
            """
            cursor.execute(sql)
            reimbs = cursor.fetchall()
            return success(reimbs, "获取成功")
    except Exception as e:
        return error(500, f"获取报销申请失败: {str(e)}")


@app.put("/reimbursements/{reimbursement_id}", summary="更新报销申请")
async def update_reimbursement(reimbursement_id: int, data: Reimbursement, token: str = Depends(verify_token)):
    """D级模块：更新报销申请"""
    try:
        with get_db_cursor() as cursor:
            sql = "SELECT status FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (reimbursement_id,))
            reimb = cursor.fetchone()
            
            if not reimb:
                return error(404, "报销申请不存在")
            
            if reimb['status'] != "pending":
                return error(400, "只能更新待审批的申请")
            
            sql = """
                UPDATE reimbursements 
                SET amount = %s, reason = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(sql, (data.amount, data.reason, reimbursement_id))
            
            sql = "SELECT * FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (reimbursement_id,))
            updated_reimb = cursor.fetchone()
            
            return success(updated_reimb, "更新成功")
    except Exception as e:
        return error(500, f"更新报销申请失败: {str(e)}")


@app.delete("/reimbursements/{reimbursement_id}", summary="删除报销申请")
async def delete_reimbursement(reimbursement_id: int, token: str = Depends(verify_token)):
    """D级模块：删除报销申请"""
    try:
        with get_db_cursor() as cursor:
            # 检查是否有依赖的审批记录
            sql = "SELECT id FROM dept_approvals WHERE reimbursement_id = %s LIMIT 1"
            cursor.execute(sql, (reimbursement_id,))
            if cursor.fetchone():
                return error(400, "该申请已有部门审批记录，无法删除")
            
            sql = "SELECT id FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (reimbursement_id,))
            if not cursor.fetchone():
                return error(404, "报销申请不存在")
            
            sql = "DELETE FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (reimbursement_id,))
            
            return success(None, "删除成功")
    except Exception as e:
        return error(500, f"删除报销申请失败: {str(e)}")


@app.post("/dept-approvals", summary="创建部门审批")
async def create_dept_approval(approval: DeptApproval, token: str = Depends(verify_token)):
    """C级模块：部门审批"""
    try:
        with get_db_cursor() as cursor:
            # 检查报销申请是否存在
            sql = "SELECT status FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (approval.reimbursement_id,))
            reimb = cursor.fetchone()
            
            if not reimb:
                return error(404, "报销申请不存在")
            
            if reimb['status'] != "pending":
                return error(400, "该申请已被处理")
            
            # 创建部门审批
            sql = """
                INSERT INTO dept_approvals (reimbursement_id, approver_id, status, comment, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (approval.reimbursement_id, approval.approver_id, approval.status, approval.comment))
            
            # 更新报销申请状态
            new_status = "dept_approved" if approval.status == "approved" else "dept_rejected"
            sql = "UPDATE reimbursements SET status = %s, updated_at = NOW() WHERE id = %s"
            cursor.execute(sql, (new_status, approval.reimbursement_id))
            
            return success({"status": approval.status}, "部门审批创建成功")
    except Exception as e:
        return error(500, f"创建部门审批失败: {str(e)}")


@app.get("/dept-approvals", summary="获取部门审批列表")
async def get_dept_approvals(reimbursement_id: Optional[int] = None, token: str = Depends(verify_token)):
    """C级模块：获取部门审批列表"""
    try:
        with get_db_cursor() as cursor:
            if reimbursement_id is not None:
                sql = "SELECT * FROM dept_approvals WHERE reimbursement_id = %s"
                cursor.execute(sql, (reimbursement_id,))
            else:
                sql = "SELECT * FROM dept_approvals ORDER BY id DESC"
                cursor.execute(sql)
            
            approvals = cursor.fetchall()
            return success(approvals, "获取成功")
    except Exception as e:
        return error(500, f"获取部门审批失败: {str(e)}")


@app.post("/finance-approvals", summary="创建财务审批")
async def create_finance_approval(approval: FinanceApproval, token: str = Depends(verify_token)):
    """B级模块：财务审批"""
    try:
        with get_db_cursor() as cursor:
            # 检查报销申请是否存在
            sql = "SELECT status FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (approval.reimbursement_id,))
            reimb = cursor.fetchone()
            
            if not reimb:
                return error(404, "报销申请不存在")
            
            # 检查部门审批是否存在且通过
            sql = "SELECT status FROM dept_approvals WHERE id = %s AND reimbursement_id = %s"
            cursor.execute(sql, (approval.dept_approval_id, approval.reimbursement_id))
            dept_approval = cursor.fetchone()
            
            if not dept_approval:
                return error(404, "部门审批不存在")
            
            if dept_approval['status'] != "approved":
                return error(400, "部门审批未通过，无法进行财务审批")
            
            # 创建财务审批
            sql = """
                INSERT INTO finance_approvals (reimbursement_id, dept_approval_id, approver_id, status, comment, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (approval.reimbursement_id, approval.dept_approval_id, 
                               approval.approver_id, approval.status, approval.comment))
            
            # 更新报销申请状态
            new_status = "finance_approved" if approval.status == "approved" else "finance_rejected"
            sql = "UPDATE reimbursements SET status = %s, updated_at = NOW() WHERE id = %s"
            cursor.execute(sql, (new_status, approval.reimbursement_id))
            
            return success({"status": approval.status}, "财务审批创建成功")
    except Exception as e:
        return error(500, f"创建财务审批失败: {str(e)}")


@app.get("/finance-approvals", summary="获取财务审批列表")
async def get_finance_approvals(reimbursement_id: Optional[int] = None, token: str = Depends(verify_token)):
    """B级模块：获取财务审批列表"""
    try:
        with get_db_cursor() as cursor:
            if reimbursement_id is not None:
                sql = "SELECT * FROM finance_approvals WHERE reimbursement_id = %s"
                cursor.execute(sql, (reimbursement_id,))
            else:
                sql = "SELECT * FROM finance_approvals ORDER BY id DESC"
                cursor.execute(sql)
            
            approvals = cursor.fetchall()
            return success(approvals, "获取成功")
    except Exception as e:
        return error(500, f"获取财务审批失败: {str(e)}")


@app.post("/ceo-approvals", summary="创建总经理审批")
async def create_ceo_approval(approval: CEOApproval, token: str = Depends(verify_token)):
    """A级模块：总经理审批"""
    try:
        with get_db_cursor() as cursor:
            # 检查报销申请是否存在
            sql = "SELECT status FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (approval.reimbursement_id,))
            reimb = cursor.fetchone()
            
            if not reimb:
                return error(404, "报销申请不存在")
            
            # 检查财务审批是否存在且通过
            sql = "SELECT status FROM finance_approvals WHERE id = %s AND reimbursement_id = %s"
            cursor.execute(sql, (approval.finance_approval_id, approval.reimbursement_id))
            finance_approval = cursor.fetchone()
            
            if not finance_approval:
                return error(404, "财务审批不存在")
            
            if finance_approval['status'] != "approved":
                return error(400, "财务审批未通过，无法进行总经理审批")
            
            # 创建总经理审批
            sql = """
                INSERT INTO ceo_approvals (reimbursement_id, finance_approval_id, approver_id, status, comment, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (approval.reimbursement_id, approval.finance_approval_id,
                               approval.approver_id, approval.status, approval.comment))
            
            # 更新报销申请状态
            new_status = "ceo_approved" if approval.status == "approved" else "ceo_rejected"
            sql = "UPDATE reimbursements SET status = %s, updated_at = NOW() WHERE id = %s"
            cursor.execute(sql, (new_status, approval.reimbursement_id))
            
            return success({"status": approval.status}, "总经理审批创建成功")
    except Exception as e:
        return error(500, f"创建总经理审批失败: {str(e)}")


@app.get("/ceo-approvals", summary="获取总经理审批列表")
async def get_ceo_approvals(reimbursement_id: Optional[int] = None, token: str = Depends(verify_token)):
    """A级模块：获取总经理审批列表"""
    try:
        with get_db_cursor() as cursor:
            if reimbursement_id is not None:
                sql = "SELECT * FROM ceo_approvals WHERE reimbursement_id = %s"
                cursor.execute(sql, (reimbursement_id,))
            else:
                sql = "SELECT * FROM ceo_approvals ORDER BY id DESC"
                cursor.execute(sql)
            
            approvals = cursor.fetchall()
            return success(approvals, "获取成功")
    except Exception as e:
        return error(500, f"获取总经理审批失败: {str(e)}")


@app.get("/workflow/{reimbursement_id}", summary="获取完整审批流程")
async def get_workflow(reimbursement_id: int, token: str = Depends(verify_token)):
    """获取完整的审批流程信息"""
    try:
        with get_db_cursor() as cursor:
            # 获取报销申请
            sql = "SELECT * FROM reimbursements WHERE id = %s"
            cursor.execute(sql, (reimbursement_id,))
            reimbursement = cursor.fetchone()
            
            if not reimbursement:
                return error(404, "报销申请不存在")
            
            # 获取各级审批
            sql = "SELECT * FROM dept_approvals WHERE reimbursement_id = %s"
            cursor.execute(sql, (reimbursement_id,))
            dept_approval = cursor.fetchone()
            
            sql = "SELECT * FROM finance_approvals WHERE reimbursement_id = %s"
            cursor.execute(sql, (reimbursement_id,))
            finance_approval = cursor.fetchone()
            
            sql = "SELECT * FROM ceo_approvals WHERE reimbursement_id = %s"
            cursor.execute(sql, (reimbursement_id,))
            ceo_approval = cursor.fetchone()
            
            return success(
                {
                    "reimbursement": reimbursement,
                    "dept_approval": dept_approval,
                    "finance_approval": finance_approval,
                    "ceo_approval": ceo_approval,
                },
                "获取成功",
            )
    except Exception as e:
        return error(500, f"获取审批流程失败: {str(e)}")


# ========================
# 启动初始化
# ========================

@app.get("/startup", summary="初始化数据")
async def startup_event():
    """初始化测试数据"""
    try:
        with get_db_cursor() as cursor:
            # 清空现有数据（保留表结构）
            tables = ['ceo_approvals', 'finance_approvals', 'dept_approvals', 
                     'reimbursements', 'orders', 'files', 'data_submissions', 
                     'products', 'users']
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except:
                    pass
            
            # 初始化用户数据
            users_data = [
                (1, 'testuser', 'test@example.com', 'Test User', 
                 '482c811da5d5b4bc6d497ffa98491e38', 'user', 'active'),
                (2, 'admin', 'admin@example.com', 'Administrator',
                 '21232f297a57a5a743894a0e4a801fc3', 'admin', 'active'),
                (3, 'dept_manager', 'dept@example.com', 'Department Manager',
                 '482c811da5d5b4bc6d497ffa98491e38', 'manager', 'active'),
                (4, 'finance_manager', 'finance@example.com', 'Finance Manager',
                 '482c811da5d5b4bc6d497ffa98491e38', 'finance', 'active'),
                (5, 'ceo', 'ceo@example.com', 'CEO',
                 '482c811da5d5b4bc6d497ffa98491e38', 'ceo', 'active'),
            ]
            
            for user in users_data:
                sql = """
                    INSERT INTO users (id, username, email, full_name, password, role, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    ON DUPLICATE KEY UPDATE 
                    email = VALUES(email), full_name = VALUES(full_name), 
                    password = VALUES(password), role = VALUES(role), status = VALUES(status)
                """
                cursor.execute(sql, user)
            
            # 初始化产品数据
            products_data = [
                ('笔记本电脑', 5999.00, '高性能商务笔记本', 100),
                ('无线鼠标', 99.00, '人体工学设计', 200),
                ('机械键盘', 399.00, 'RGB背光', 150),
                ('显示器', 1299.00, '27英寸4K', 50),
            ]
            
            for product in products_data:
                sql = """
                    INSERT INTO products (name, price, description, stock, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                """
                cursor.execute(sql, product)
            
            return success({"message": "数据初始化成功"}, "初始化完成")
    except Exception as e:
        return error(500, f"初始化失败: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
