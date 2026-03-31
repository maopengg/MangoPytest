from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import uvicorn
import uuid
from datetime import datetime
import hashlib
from pydantic import BaseModel
from fastapi import Request, UploadFile, File

app = FastAPI(title="Mock API Service", description="用于API自动化测试的模拟后端服务")

# ========================
# 中间件
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
# 模拟数据库
# ========================

users_db = []
users_db_1 = []
products_db = []
orders_db = []


# ========================
# 模型定义
# ========================


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    full_name: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Product(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    description: Optional[str] = None


class Order(BaseModel):
    id: Optional[int] = None
    product_id: int
    quantity: int
    user_id: int


class DataModel(BaseModel):
    name: str
    value: str | int


users_db_1.extend(
    [
        User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="482c811da5d5b4bc6d497ffa98491e38",
        ),
        User(
            id=2,
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            password="21232f297a57a5a743894a0e4a801fc3",
        ),
    ]
)
users_db.extend(
    [
        User(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="482c811da5d5b4bc6d497ffa98491e38",
        ),
        User(
            id=2,
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            password="21232f297a57a5a743894a0e4a801fc3",
        ),
    ]
)


# ========================
# 工具函数
# ========================


def get_user_by_username(username: str):
    for user in users_db_1:
        if user.username == username:
            return user
    return None


async def verify_token(x_token: str = Header(None)):
    if x_token is None:
        raise HTTPException(status_code=401, detail="未提供token")

    if not x_token.startswith("mock_token_"):
        raise HTTPException(status_code=401, detail="无效的token")

    return x_token


def success(data=None, message="成功"):
    return {"code": 200, "message": message, "data": data}


def error(code, message):
    return {"code": code, "message": message, "data": None}


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

    user = get_user_by_username(user_login.username)

    if not user:
        return error(401, "用户名或密码错误")

    if user_login.password != user.password:
        return error(402, "用户名或密码错误")

    return success(
        {
            "user_id": user.id,
            "username": user.username,
            "token": f"mock_token_{uuid.uuid4()}",
        },
        "登录成功",
    )


# ========================
# 2. 注册
# ========================


@app.post("/auth/register", summary="用户注册")
async def register(user: UserCreate):
    if user.username.strip() == "" or user.password.strip() == "":
        return error(400, "用户名或密码不能为空")

    if get_user_by_username(user.username):
        return error(400, "用户名已存在")

    new_user = User(
        id=len(users_db) + 1,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        password=hashlib.md5(user.password.encode()).hexdigest(),
    )

    users_db.append(new_user)

    return success(new_user, "注册成功")


# ========================
# 3. 用户管理
# ========================


@app.get("/users", summary="获取用户")
async def get_users(id: Optional[int] = None, token: str = Depends(verify_token)):
    if id is not None:
        for user in users_db:
            if user.id == id:
                return success(user, "获取成功")
        return error(404, "用户不存在")

    return success(users_db, "获取成功")


@app.put("/users", summary="更新用户")
async def update_user(id: int, user: User, token: str = Depends(verify_token)):
    for i, u in enumerate(users_db):
        if u.id == id:
            user.id = id
            users_db[i] = user
            return success(user, "更新成功")

    return error(404, "用户不存在")


@app.delete("/users", summary="删除用户")
async def delete_user(id: int, token: str = Depends(verify_token)):
    for i, user in enumerate(users_db):
        if user.id == id:
            del users_db[i]
            return success(None, "删除成功")

    return error(404, "用户不存在")


# ========================
# 产品管理
# ========================


@app.post("/products")
async def create_product(product: Product, token: str = Depends(verify_token)):
    product.id = len(products_db) + 1
    products_db.append(product)
    return success(product, "创建成功")


@app.get("/products")
async def get_products(id: Optional[int] = None, token: str = Depends(verify_token)):
    if id is not None:
        for product in products_db:
            if product.id == id:
                return success(product, "获取成功")
        return error(404, "产品不存在")

    return success(products_db, "获取成功")


@app.put("/products")
async def update_product(id: int, product: Product, token: str = Depends(verify_token)):
    for i, p in enumerate(products_db):
        if p.id == id:
            product.id = id
            products_db[i] = product
            return success(product, "更新成功")

    return error(404, "产品不存在")


@app.delete("/products")
async def delete_product(id: int, token: str = Depends(verify_token)):
    for i, product in enumerate(products_db):
        if product.id == id:
            del products_db[i]
            return success(None, "删除成功")

    return error(404, "产品不存在")


# ========================
# 订单管理
# ========================


@app.post("/orders")
async def create_order(order: Order, token: str = Depends(verify_token)):
    order.id = len(orders_db) + 1
    orders_db.append(order)
    return success(order, "创建成功")


@app.get("/orders")
async def get_orders(token: str = Depends(verify_token)):
    return success(orders_db, "获取成功")


@app.get("/orders/{order_id}")
async def get_order(order_id: int, token: str = Depends(verify_token)):
    for order in orders_db:
        if order.id == order_id:
            return success(order, "获取成功")
    return error(404, "订单不存在")


@app.put("/orders")
async def update_order(id: int, order: Order, token: str = Depends(verify_token)):
    for i, o in enumerate(orders_db):
        if o.id == id:
            order.id = id
            orders_db[i] = order
            return success(order, "更新成功")

    return error(404, "订单不存在")


@app.delete("/orders")
async def delete_order(id: int, token: str = Depends(verify_token)):
    for i, order in enumerate(orders_db):
        if order.id == id:
            del orders_db[i]
            return success(None, "删除成功")

    return error(404, "订单不存在")


# ========================
# 数据提交
# ========================


@app.post("/api/data")
async def submit_data(request: Request, token: str = Depends(verify_token)):
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

    return success(
        {"name": name, "value": int(value), "timestamp": datetime.now().isoformat()},
        "数据提交成功",
    )


# ========================
# 上传文件
# ========================
@app.post("/upload")
async def upload_file(file: UploadFile = File(...), token: str = Depends(verify_token)):
    try:
        file_content = await file.read()

        return success(
            {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(file_content),
                "file_id": str(uuid.uuid4()),
            },
            "上传成功",
        )

    except Exception:
        return error(500, "文件处理失败")


# ========================
# 健康检查
# ========================


@app.get("/health")
async def health_check(token: str = Depends(verify_token)):
    return success(
        {"status": "healthy", "timestamp": datetime.now().isoformat()}, "服务正常运行"
    )


# ========================
# 服务器信息
# ========================


@app.get("/info")
async def server_info(token: str = Depends(verify_token)):
    return success(
        {
            "app_name": "Mock API Service",
            "version": "1.0.0",
            "framework": "FastAPI",
            "python_version": "3.10",
        },
        "获取成功",
    )


# ========================
# 审批流模块 - 4级审批
# D级：报销申请 (Reimbursement)
# C级：部门审批 (DeptApproval)
# B级：财务审批 (FinanceApproval)
# A级：总经理审批 (CEOApproval)
# ========================

# 模拟数据库
reimbursements_db = []
dept_approvals_db = []
finance_approvals_db = []
ceo_approvals_db = []


class Reimbursement(BaseModel):
    """D级：报销申请"""

    id: Optional[int] = None
    user_id: int
    amount: float
    reason: str
    status: str = (
        "pending"  # pending, dept_approved, dept_rejected, finance_approved, finance_rejected, ceo_approved, ceo_rejected
    )
    created_at: Optional[str] = None


class DeptApproval(BaseModel):
    """C级：部门审批"""

    id: Optional[int] = None
    reimbursement_id: int
    approver_id: int
    status: str  # approved, rejected
    comment: Optional[str] = None
    created_at: Optional[str] = None


class FinanceApproval(BaseModel):
    """B级：财务审批"""

    id: Optional[int] = None
    reimbursement_id: int
    dept_approval_id: int
    approver_id: int
    status: str  # approved, rejected
    comment: Optional[str] = None
    created_at: Optional[str] = None


class CEOApproval(BaseModel):
    """A级：总经理审批"""

    id: Optional[int] = None
    reimbursement_id: int
    finance_approval_id: int
    approver_id: int
    status: str  # approved, rejected
    comment: Optional[str] = None
    created_at: Optional[str] = None


# ========================
# D级：报销申请接口
# ========================


@app.post("/reimbursements", summary="创建报销申请")
async def create_reimbursement(
    reimbursement: Reimbursement, token: str = Depends(verify_token)
):
    """D级模块：创建报销申请"""
    if reimbursement.amount <= 0:
        return error(400, "报销金额必须大于0")

    if not reimbursement.reason or reimbursement.reason.strip() == "":
        return error(400, "报销原因不能为空")

    reimbursement.id = len(reimbursements_db) + 1
    reimbursement.status = "pending"
    reimbursement.created_at = datetime.now().isoformat()
    reimbursements_db.append(reimbursement)

    return success(reimbursement, "报销申请创建成功")


@app.get("/reimbursements", summary="获取报销申请")
async def get_reimbursements(
    id: Optional[int] = None, token: str = Depends(verify_token)
):
    """D级模块：获取报销申请列表或单个申请"""
    if id is not None:
        for r in reimbursements_db:
            if r.id == id:
                return success(r, "获取成功")
        return error(404, "报销申请不存在")

    return success(reimbursements_db, "获取成功")


@app.put("/reimbursements/{reimbursement_id}", summary="更新报销申请")
async def update_reimbursement(
    reimbursement_id: int, data: Reimbursement, token: str = Depends(verify_token)
):
    """D级模块：更新报销申请（仅在pending状态可更新）"""
    for i, r in enumerate(reimbursements_db):
        if r.id == reimbursement_id:
            if r.status != "pending":
                return error(400, "只能更新待审批的申请")

            data.id = reimbursement_id
            data.status = r.status
            data.created_at = r.created_at
            reimbursements_db[i] = data
            return success(data, "更新成功")

    return error(404, "报销申请不存在")


@app.delete("/reimbursements/{reimbursement_id}", summary="删除报销申请")
async def delete_reimbursement(
    reimbursement_id: int, token: str = Depends(verify_token)
):
    """D级模块：删除报销申请"""
    for i, r in enumerate(reimbursements_db):
        if r.id == reimbursement_id:
            # 检查是否有依赖的审批记录
            for da in dept_approvals_db:
                if da.reimbursement_id == reimbursement_id:
                    return error(400, "该申请已有部门审批记录，无法删除")

            del reimbursements_db[i]
            return success(None, "删除成功")

    return error(404, "报销申请不存在")


# ========================
# C级：部门审批接口
# ========================


@app.post("/dept-approvals", summary="创建部门审批")
async def create_dept_approval(
    approval: DeptApproval, token: str = Depends(verify_token)
):
    """C级模块：部门审批（依赖D级报销申请）"""
    # 检查报销申请是否存在
    reimbursement = None
    for r in reimbursements_db:
        if r.id == approval.reimbursement_id:
            reimbursement = r
            break

    if not reimbursement:
        return error(404, "报销申请不存在")

    if reimbursement.status != "pending":
        return error(400, "该申请已被处理")

    # 创建部门审批
    approval.id = len(dept_approvals_db) + 1
    approval.created_at = datetime.now().isoformat()
    dept_approvals_db.append(approval)

    # 更新报销申请状态
    if approval.status == "approved":
        reimbursement.status = "dept_approved"
    else:
        reimbursement.status = "dept_rejected"

    return success(approval, "部门审批创建成功")


@app.get("/dept-approvals", summary="获取部门审批")
async def get_dept_approvals(
    reimbursement_id: Optional[int] = None, token: str = Depends(verify_token)
):
    """C级模块：获取部门审批列表"""
    if reimbursement_id is not None:
        approvals = [
            a for a in dept_approvals_db if a.reimbursement_id == reimbursement_id
        ]
        return success(approvals, "获取成功")

    return success(dept_approvals_db, "获取成功")


@app.put("/dept-approvals/{approval_id}", summary="更新部门审批")
async def update_dept_approval(
    approval_id: int, data: DeptApproval, token: str = Depends(verify_token)
):
    """C级模块：更新部门审批"""
    for i, a in enumerate(dept_approvals_db):
        if a.id == approval_id:
            # 检查是否已有财务审批
            for fa in finance_approvals_db:
                if fa.dept_approval_id == approval_id:
                    return error(400, "该审批已有财务审批记录，无法修改")

            data.id = approval_id
            data.created_at = a.created_at
            dept_approvals_db[i] = data

            # 更新报销申请状态
            for r in reimbursements_db:
                if r.id == data.reimbursement_id:
                    if data.status == "approved":
                        r.status = "dept_approved"
                    else:
                        r.status = "dept_rejected"
                    break

            return success(data, "更新成功")

    return error(404, "部门审批不存在")


# ========================
# B级：财务审批接口
# ========================


@app.post("/finance-approvals", summary="创建财务审批")
async def create_finance_approval(
    approval: FinanceApproval, token: str = Depends(verify_token)
):
    """B级模块：财务审批（依赖C级部门审批）"""
    # 检查报销申请是否存在
    reimbursement = None
    for r in reimbursements_db:
        if r.id == approval.reimbursement_id:
            reimbursement = r
            break

    if not reimbursement:
        return error(404, "报销申请不存在")

    # 检查部门审批是否存在且通过
    dept_approval = None
    for da in dept_approvals_db:
        if (
            da.id == approval.dept_approval_id
            and da.reimbursement_id == approval.reimbursement_id
        ):
            dept_approval = da
            break

    if not dept_approval:
        return error(404, "部门审批不存在")

    if dept_approval.status != "approved":
        return error(400, "部门审批未通过，无法进行财务审批")

    if reimbursement.status not in [
        "dept_approved",
        "finance_approved",
        "finance_rejected",
    ]:
        return error(400, "该申请状态不允许财务审批")

    # 创建财务审批
    approval.id = len(finance_approvals_db) + 1
    approval.created_at = datetime.now().isoformat()
    finance_approvals_db.append(approval)

    # 更新报销申请状态
    if approval.status == "approved":
        reimbursement.status = "finance_approved"
    else:
        reimbursement.status = "finance_rejected"

    return success(approval, "财务审批创建成功")


@app.get("/finance-approvals", summary="获取财务审批")
async def get_finance_approvals(
    reimbursement_id: Optional[int] = None, token: str = Depends(verify_token)
):
    """B级模块：获取财务审批列表"""
    if reimbursement_id is not None:
        approvals = [
            a for a in finance_approvals_db if a.reimbursement_id == reimbursement_id
        ]
        return success(approvals, "获取成功")

    return success(finance_approvals_db, "获取成功")


@app.put("/finance-approvals/{approval_id}", summary="更新财务审批")
async def update_finance_approval(
    approval_id: int, data: FinanceApproval, token: str = Depends(verify_token)
):
    """B级模块：更新财务审批"""
    for i, a in enumerate(finance_approvals_db):
        if a.id == approval_id:
            # 检查是否已有总经理审批
            for ca in ceo_approvals_db:
                if ca.finance_approval_id == approval_id:
                    return error(400, "该审批已有总经理审批记录，无法修改")

            data.id = approval_id
            data.created_at = a.created_at
            finance_approvals_db[i] = data

            # 更新报销申请状态
            for r in reimbursements_db:
                if r.id == data.reimbursement_id:
                    if data.status == "approved":
                        r.status = "finance_approved"
                    else:
                        r.status = "finance_rejected"
                    break

            return success(data, "更新成功")

    return error(404, "财务审批不存在")


# ========================
# A级：总经理审批接口
# ========================


@app.post("/ceo-approvals", summary="创建总经理审批")
async def create_ceo_approval(
    approval: CEOApproval, token: str = Depends(verify_token)
):
    """A级模块：总经理审批（依赖B级财务审批）"""
    # 检查报销申请是否存在
    reimbursement = None
    for r in reimbursements_db:
        if r.id == approval.reimbursement_id:
            reimbursement = r
            break

    if not reimbursement:
        return error(404, "报销申请不存在")

    # 检查财务审批是否存在且通过
    finance_approval = None
    for fa in finance_approvals_db:
        if (
            fa.id == approval.finance_approval_id
            and fa.reimbursement_id == approval.reimbursement_id
        ):
            finance_approval = fa
            break

    if not finance_approval:
        return error(404, "财务审批不存在")

    if finance_approval.status != "approved":
        return error(400, "财务审批未通过，无法进行总经理审批")

    if reimbursement.status not in ["finance_approved", "ceo_approved", "ceo_rejected"]:
        return error(400, "该申请状态不允许总经理审批")

    # 创建总经理审批
    approval.id = len(ceo_approvals_db) + 1
    approval.created_at = datetime.now().isoformat()
    ceo_approvals_db.append(approval)

    # 更新报销申请状态
    if approval.status == "approved":
        reimbursement.status = "ceo_approved"
    else:
        reimbursement.status = "ceo_rejected"

    return success(approval, "总经理审批创建成功")


@app.get("/ceo-approvals", summary="获取总经理审批")
async def get_ceo_approvals(
    reimbursement_id: Optional[int] = None, token: str = Depends(verify_token)
):
    """A级模块：获取总经理审批列表"""
    if reimbursement_id is not None:
        approvals = [
            a for a in ceo_approvals_db if a.reimbursement_id == reimbursement_id
        ]
        return success(approvals, "获取成功")

    return success(ceo_approvals_db, "获取成功")


@app.get("/workflow/{reimbursement_id}", summary="获取完整审批流程")
async def get_workflow(reimbursement_id: int, token: str = Depends(verify_token)):
    """获取完整的审批流程信息"""
    # 查找报销申请
    reimbursement = None
    for r in reimbursements_db:
        if r.id == reimbursement_id:
            reimbursement = r
            break

    if not reimbursement:
        return error(404, "报销申请不存在")

    # 查找各级审批
    dept_approval = None
    for da in dept_approvals_db:
        if da.reimbursement_id == reimbursement_id:
            dept_approval = da
            break

    finance_approval = None
    for fa in finance_approvals_db:
        if fa.reimbursement_id == reimbursement_id:
            finance_approval = fa
            break

    ceo_approval = None
    for ca in ceo_approvals_db:
        if ca.reimbursement_id == reimbursement_id:
            ceo_approval = ca
            break

    return success(
        {
            "reimbursement": reimbursement,
            "dept_approval": dept_approval,
            "finance_approval": finance_approval,
            "ceo_approval": ceo_approval,
        },
        "获取成功",
    )


# ========================
# 启动初始化数据
# ========================


@app.get("/startup")
async def startup_event():
    users_db.clear()
    products_db.clear()
    orders_db.clear()
    reimbursements_db.clear()
    dept_approvals_db.clear()
    finance_approvals_db.clear()
    ceo_approvals_db.clear()

    users_db.extend(
        [
            User(
                id=1,
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                password="482c811da5d5b4bc6d497ffa98491e38",
            ),
            User(
                id=2,
                username="admin",
                email="admin@example.com",
                full_name="Administrator",
                password="21232f297a57a5a743894a0e4a801fc3",
            ),
            User(
                id=3,
                username="dept_manager",
                email="dept@example.com",
                full_name="Department Manager",
                password="482c811da5d5b4bc6d497ffa98491e38",
            ),
            User(
                id=4,
                username="finance_manager",
                email="finance@example.com",
                full_name="Finance Manager",
                password="482c811da5d5b4bc6d497ffa98491e38",
            ),
            User(
                id=5,
                username="ceo",
                email="ceo@example.com",
                full_name="CEO",
                password="482c811da5d5b4bc6d497ffa98491e38",
            ),
        ]
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
