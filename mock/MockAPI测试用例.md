# Mock API 测试用例（表格版）

## 文档信息

| 项目 | 内容 |
|------|------|
| **服务名称** | Mango Mock API Service |
| **服务地址** | http://localhost:8003 |
| **接口总数** | 33 |
| **用例总数** | 81 |

---

## 用例统计

| 模块 | 接口数 | 用例数 | P0 | P1 | P2 | 已自动化 |
|------|--------|--------|----|----|----|----------|
| 认证模块 | 2 | 10 | 2 | 7 | 1 | 10 |
| 用户管理 | 4 | 9 | 2 | 6 | 1 | 9 |
| 产品管理 | 4 | 10 | 2 | 8 | 0 | 10 |
| 订单管理 | 5 | 12 | 2 | 9 | 1 | 12 |
| 审批流程 | 11 | 22 | 5 | 14 | 3 | 22 |
| 数据与文件 | 3 | 10 | 0 | 7 | 3 | 10 |
| 系统管理 | 4 | 8 | 2 | 4 | 2 | 8 |
| **合计** | **33** | **81** | **15** | **55** | **11** | **81** |

---

## 1. 认证模块

**接口清单**: /auth/login (POST), /auth/register (POST)

| 编号 | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 预期结果 | 自动化 |
|------|----------|--------|------|----------|----------|----------|--------|
| TC-AUTH-0001 | 用户使用有效凭证登录成功 | P0 | 正向 | 服务正常；用户testuser存在 | 1.POST /auth/login<br>2.输入正确用户名密码<br>3.检查响应 | code=200；data含token | ✅已自动化 |
| TC-AUTH-0002 | 用户使用明文密码登录成功 | P1 | 正向 | 服务正常；用户存在 | 1.POST /auth/login<br>2.输入明文密码<br>3.检查响应 | code=200；系统自动MD5加密 | ✅已自动化 |
| TC-AUTH-0003 | 用户使用不存在的用户名登录 | P1 | 负向 | 服务正常 | 1.POST /auth/login<br>2.输入不存在的用户名 | code=401；用户名或密码错误 | ✅已自动化 |
| TC-AUTH-0004 | 用户使用错误密码登录 | P1 | 负向 | 服务正常；用户存在 | 1.POST /auth/login<br>2.输入错误密码 | code=402；用户名或密码错误 | ✅已自动化 |
| TC-AUTH-0005 | 用户登录-用户名为空 | P1 | 负向/边界 | 服务正常 | 1.POST /auth/login<br>2.用户名为空 | code=400；用户名或密码不能为空 | ✅已自动化 |
| TC-AUTH-0006 | 用户登录-密码为空 | P1 | 负向/边界 | 服务正常 | 1.POST /auth/login<br>2.密码为空 | code=400；用户名或密码不能为空 | ✅已自动化 |
| TC-AUTH-0007 | 新用户注册成功 | P0 | 正向 | 服务正常；用户名未注册 | 1.POST /auth/register<br>2.输入完整注册信息<br>3.检查响应和数据库 | code=200；数据库新增记录 | ✅已自动化 |
| TC-AUTH-0008 | 注册-用户名已存在 | P1 | 负向 | 服务正常；用户已存在 | 1.POST /auth/register<br>2.输入已存在用户名 | code=400；用户名已存在 | ✅已自动化 |
| TC-AUTH-0009 | 注册-用户名为空 | P1 | 负向/边界 | 服务正常 | 1.POST /auth/register<br>2.用户名为空 | code=400；用户名或密码不能为空 | ✅已自动化 |
| TC-AUTH-0010 | 注册-使用MD5密码注册 | P2 | 正向 | 服务正常 | 1.POST /auth/register<br>2.密码传MD5值 | code=200；不做二次加密 | ✅已自动化 |

---

## 2. 用户管理

**接口清单**: /users (GET), /users/{id} (GET/PUT/DELETE)

| 编号 | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 预期结果 | 自动化 |
|------|----------|--------|------|----------|----------|----------|--------|
| TC-USER-0001 | 获取用户列表成功 | P0 | 正向 | 服务正常；有Token；有用户数据 | 1.GET /users<br>2.携带Token | code=200；data为数组；无password字段 | ✅已自动化 |
| TC-USER-0002 | 根据ID获取用户成功 | P0 | 正向 | 服务正常；有Token；ID=1存在 | 1.GET /users?id=1 | code=200；单个用户对象 | ✅已自动化 |
| TC-USER-0003 | 获取不存在的用户 | P1 | 负向 | 服务正常；有Token | 1.GET /users?id=99999 | code=404；用户不存在 | ✅已自动化 |
| TC-USER-0004 | 更新用户信息成功 | P1 | 正向 | 服务正常；有Token；ID=1存在 | 1.PUT /users/1<br>2.输入更新信息 | code=200；data反映更新值 | ✅已自动化 |
| TC-USER-0005 | 更新不存在的用户 | P1 | 负向 | 服务正常；有Token | 1.PUT /users/99999 | code=404；用户不存在 | ✅已自动化 |
| TC-USER-0006 | 删除用户成功 | P1 | 正向 | 服务正常；有Token；有测试用户 | 1.DELETE /users/{id} | code=200；status变deleted | ✅已自动化 |
| TC-USER-0007 | 未授权访问用户列表 | P1 | 负向/安全 | 服务正常 | 1.GET /users<br>2.无Token | HTTP 401；未提供token | ✅已自动化 |
| TC-USER-0008 | 使用无效Token访问 | P1 | 负向/安全 | 服务正常 | 1.GET /users<br>2.Token=invalid | HTTP 401；无效的token | ✅已自动化 |
| TC-USER-0009 | 使用Authorization头传递Token | P2 | 正向 | 服务正常；有Token | 1.GET /users<br>2.Authorization: Bearer {token} | code=200；正常返回 | ✅已自动化 |

---

## 3. 产品管理

**接口清单**: /products (POST/GET), /products/{id} (PUT/DELETE)

| 编号 | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 预期结果 | 自动化 |
|------|----------|--------|------|----------|----------|----------|--------|
| TC-PROD-0001 | 创建产品成功 | P0 | 正向 | 服务正常；有Token | 1.POST /products<br>2.输入产品信息 | code=200；data含id等字段 | ✅已自动化 |
| TC-PROD-0002 | 获取产品列表成功 | P0 | 正向 | 服务正常；有Token；有数据 | 1.GET /products | code=200；数组按id倒序 | ✅已自动化 |
| TC-PROD-0003 | 根据ID获取产品成功 | P1 | 正向 | 服务正常；有Token；ID=1存在 | 1.GET /products?id=1 | code=200；单个产品对象 | ✅已自动化 |
| TC-PROD-0004 | 更新产品成功 | P1 | 正向 | 服务正常；有Token；ID=1存在 | 1.PUT /products/1 | code=200；更新成功 | ✅已自动化 |
| TC-PROD-0005 | 删除产品成功 | P1 | 正向 | 服务正常；有Token；有测试产品 | 1.DELETE /products/{id} | code=200；删除成功 | ✅已自动化 |
| TC-PROD-0006 | 创建产品-名称为空 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /products<br>2.name为空 | 根据实现判断 | ✅已自动化 |
| TC-PROD-0007 | 创建产品-价格为负数 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /products<br>2.price为负 | 根据实现判断 | ✅已自动化 |
| TC-PROD-0008 | 创建产品-库存为负数 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /products<br>2.stock为负 | 根据实现判断 | ✅已自动化 |
| TC-PROD-0009 | 获取不存在的产品 | P1 | 负向 | 服务正常；有Token | 1.GET /products?id=99999 | code=404；产品不存在 | ✅已自动化 |
| TC-PROD-0010 | 删除不存在的产品 | P1 | 负向 | 服务正常；有Token | 1.DELETE /products/99999 | code=404；产品不存在 | ✅已自动化 |

---

## 4. 订单管理

**接口清单**: /orders (POST/GET), /orders/{id} (GET/PUT/DELETE)

| 编号 | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 预期结果 | 自动化 |
|------|----------|--------|------|----------|----------|----------|--------|
| TC-ORDER-0001 | 创建订单成功 | P0 | 正向/集成 | 服务正常；有Token；产品库存充足 | 1.记录库存<br>2.POST /orders<br>3.检查响应和库存 | code=200；库存扣减 | ✅已自动化 |
| TC-ORDER-0002 | 获取订单列表成功 | P0 | 正向 | 服务正常；有Token；有订单数据 | 1.GET /orders | code=200；含关联信息 | ✅已自动化 |
| TC-ORDER-0003 | 根据ID获取订单成功 | P1 | 正向 | 服务正常；有Token；ID=1存在 | 1.GET /orders/1 | code=200；完整订单信息 | ✅已自动化 |
| TC-ORDER-0004 | 更新订单成功 | P1 | 正向 | 服务正常；有Token；ID=1存在 | 1.PUT /orders/1 | code=200；更新成功 | ✅已自动化 |
| TC-ORDER-0005 | 删除订单成功 | P1 | 正向 | 服务正常；有Token；有测试订单 | 1.DELETE /orders/{id} | code=200；删除成功 | ✅已自动化 |
| TC-ORDER-0006 | 创建订单-产品不存在 | P1 | 负向 | 服务正常；有Token | 1.POST /orders<br>2.product_id不存在 | code=404；产品不存在 | ✅已自动化 |
| TC-ORDER-0007 | 创建订单-库存不足 | P1 | 负向 | 服务正常；有Token | 1.POST /orders<br>2.quantity超库存 | code=400；库存不足 | ✅已自动化 |
| TC-ORDER-0008 | 创建订单-数量为0 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /orders<br>2.quantity=0 | 根据实现判断 | ✅已自动化 |
| TC-ORDER-0009 | 获取不存在的订单 | P1 | 负向 | 服务正常；有Token | 1.GET /orders/99999 | code=404；订单不存在 | ✅已自动化 |
| TC-ORDER-0010 | 更新不存在的订单 | P1 | 负向 | 服务正常；有Token | 1.PUT /orders/99999 | code=404；订单不存在 | ✅已自动化 |
| TC-ORDER-0011 | 删除不存在的订单 | P1 | 负向 | 服务正常；有Token | 1.DELETE /orders/99999 | code=404；订单不存在 | ✅已自动化 |
| TC-ORDER-0012 | 订单金额计算准确性 | P2 | 正向 | 服务正常；有Token | 1.创建多个订单<br>2.检查total_amount | 金额=单价×数量 | ✅已自动化 |

---

## 5. 审批流程

**接口清单**: /reimbursements (POST/GET/PUT/DELETE), /dept-approvals (POST/GET), /finance-approvals (POST/GET), /ceo-approvals (POST/GET), /workflow/{id} (GET)

| 编号 | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 预期结果 | 自动化 |
|------|----------|--------|------|----------|----------|----------|--------|
| TC-APPROVAL-0001 | 创建报销申请成功 | P0 | 正向 | 服务正常；有Token；有申请人 | 1.POST /reimbursements | code=200；status=pending | ✅已自动化 |
| TC-APPROVAL-0002 | 创建报销-金额小于等于0 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /reimbursements<br>2.amount=0 | code=400；金额必须大于0 | ✅已自动化 |
| TC-APPROVAL-0003 | 创建报销-原因为空 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /reimbursements<br>2.reason为空 | code=400；原因不能为空 | ✅已自动化 |
| TC-APPROVAL-0004 | 获取报销申请列表 | P1 | 正向 | 服务正常；有Token | 1.GET /reimbursements | code=200；报销数组 | ✅已自动化 |
| TC-APPROVAL-0005 | 更新待审批的报销申请 | P1 | 正向 | 服务正常；有Token；status=pending | 1.PUT /reimbursements/{id} | code=200；更新成功 | ✅已自动化 |
| TC-APPROVAL-0006 | 更新已审批的报销申请 | P1 | 负向 | 服务正常；有Token；status≠pending | 1.PUT 已审批的申请 | code=400；只能更新待审批 | ✅已自动化 |
| TC-APPROVAL-0007 | 删除无审批记录的报销 | P1 | 正向 | 服务正常；有Token；无审批记录 | 1.DELETE /reimbursements/{id} | code=200；删除成功 | ✅已自动化 |
| TC-APPROVAL-0008 | 删除有审批记录的报销 | P1 | 负向 | 服务正常；有Token；有审批记录 | 1.DELETE 有审批的申请 | code=400；已有审批无法删除 | ✅已自动化 |
| TC-APPROVAL-0009 | 部门审批通过 | P0 | 正向 | 服务正常；有Token；status=pending | 1.POST /dept-approvals<br>2.status=approved | code=200；status=dept_approved | ✅已自动化 |
| TC-APPROVAL-0010 | 部门审批拒绝 | P1 | 正向 | 服务正常；有Token；status=pending | 1.POST /dept-approvals<br>2.status=rejected | code=200；status=dept_rejected | ✅已自动化 |
| TC-APPROVAL-0011 | 对已审批申请进行部门审批 | P1 | 负向 | 服务正常；有Token；status≠pending | 1.POST /dept-approvals | code=400；该申请已被处理 | ✅已自动化 |
| TC-APPROVAL-0012 | 财务审批通过 | P0 | 正向 | 服务正常；有Token；部门已通过 | 1.POST /finance-approvals | code=200；status=finance_approved | ✅已自动化 |
| TC-APPROVAL-0013 | 财务审批-部门未通过 | P1 | 负向 | 服务正常；有Token；部门被拒绝 | 1.POST /finance-approvals | code=400；部门审批未通过 | ✅已自动化 |
| TC-APPROVAL-0014 | 总经理审批通过 | P0 | 正向 | 服务正常；有Token；财务已通过 | 1.POST /ceo-approvals | code=200；status=ceo_approved | ✅已自动化 |
| TC-APPROVAL-0015 | 总经理审批-财务未通过 | P1 | 负向 | 服务正常；有Token；财务被拒绝 | 1.POST /ceo-approvals | code=400；财务审批未通过 | ✅已自动化 |
| TC-APPROVAL-0016 | 获取完整审批流程 | P1 | 正向 | 服务正常；有Token；有完整审批 | 1.GET /workflow/{id} | code=200；含四级审批信息 | ✅已自动化 |
| TC-APPROVAL-0017 | 完整流程-全部通过 | P0 | 正向/集成 | 服务正常；有Token；审批人就绪 | 1.创建→部门→财务→总经理 | 状态依次流转至ceo_approved | ✅已自动化 |
| TC-APPROVAL-0018 | 完整流程-部门拒绝 | P1 | 正向/集成 | 服务正常；有Token | 1.创建→部门拒绝→尝试财务 | 无法继续，返回错误 | ✅已自动化 |
| TC-APPROVAL-0019 | 完整流程-财务拒绝 | P1 | 正向/集成 | 服务正常；有Token | 1.创建→部门→财务拒绝→尝试总经理 | 无法继续，返回错误 | ✅已自动化 |
| TC-APPROVAL-0020 | 获取部门审批列表 | P2 | 正向 | 服务正常；有Token | 1.GET /dept-approvals | code=200；部门审批数组 | ✅已自动化 |
| TC-APPROVAL-0021 | 获取财务审批列表 | P2 | 正向 | 服务正常；有Token | 1.GET /finance-approvals | code=200；财务审批数组 | ✅已自动化 |
| TC-APPROVAL-0022 | 获取总经理审批列表 | P2 | 正向 | 服务正常；有Token | 1.GET /ceo-approvals | code=200；总经理审批数组 | ✅已自动化 |

---

## 6. 数据与文件

**接口清单**: /api/data (POST), /upload (POST), /download/excel (GET)

| 编号 | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 预期结果 | 自动化 |
|------|----------|--------|------|----------|----------|----------|--------|
| TC-DATA-0001 | 提交数据成功-body参数 | P1 | 正向 | 服务正常；有Token | 1.POST /api/data<br>2.JSON body | code=200；value为整数 | ✅已自动化 |
| TC-DATA-0002 | 提交数据成功-query参数 | P2 | 正向 | 服务正常；有Token | 1.POST /api/data?name=x&value=1 | code=200；提交成功 | ✅已自动化 |
| TC-DATA-0003 | 提交数据-body覆盖query | P2 | 正向 | 服务正常；有Token | 1.POST /api/data?n=v<br>2.同时发body | 使用body中的值 | ✅已自动化 |
| TC-DATA-0004 | 提交数据-name为空 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /api/data<br>2.name为空 | code=400；name不能为空 | ✅已自动化 |
| TC-DATA-0005 | 提交数据-value为空 | P1 | 负向/边界 | 服务正常；有Token | 1.POST /api/data<br>2.value为空 | code=400；value不能为空 | ✅已自动化 |
| TC-DATA-0006 | 提交数据-value非整数 | P1 | 负向 | 服务正常；有Token | 1.POST /api/data<br>2.value="abc" | code=400；value必须是整数 | ✅已自动化 |
| TC-FILE-0001 | 上传文件成功 | P1 | 正向 | 服务正常；有Token；有测试文件 | 1.POST /upload<br>2.multipart上传 | code=200；返回file_id | ✅已自动化 |
| TC-FILE-0002 | 下载Excel文件成功 | P1 | 正向 | 服务正常；有Token | 1.GET /download/excel | 返回CSV文件；3列5行数据 | ✅已自动化 |
| TC-FILE-0003 | 上传不同格式文件 | P2 | 正向/兼容 | 服务正常；有Token | 1.上传txt/json/png/xlsx | 全部上传成功；content_type正确 | ✅已自动化 |
| TC-FILE-0004 | 未选择文件上传 | P1 | 负向 | 服务正常；有Token | 1.POST /upload<br>2.无文件 | HTTP 422；缺少文件参数 | ✅已自动化 |

---

## 7. 系统管理

**接口清单**: /health (GET), /info (GET), /startup (GET), / (GET)

| 编号 | 用例标题 | 优先级 | 类型 | 前置条件 | 测试步骤 | 预期结果 | 自动化 |
|------|----------|--------|------|----------|----------|----------|--------|
| TC-SYS-0001 | 健康检查成功 | P0 | 正向 | 服务正常；有Token | 1.GET /health<br>2.带Token和自定义头 | code=200；status=healthy | ✅已自动化 |
| TC-SYS-0002 | 健康检查-缺少自定义头 | P1 | 负向/安全 | 服务正常；有Token | 1.GET /health<br>2.只带Token | HTTP 403；缺少X-Custom-Key | ✅已自动化 |
| TC-SYS-0003 | 健康检查-自定义密钥错误 | P1 | 负向/安全 | 服务正常；有Token | 1.GET /health<br>2.X-Custom-Key错误 | HTTP 403；无效的X-Custom-Key | ✅已自动化 |
| TC-SYS-0004 | 获取服务器信息成功 | P1 | 正向 | 服务正常；有Token | 1.GET /info<br>2.带Token和自定义头 | code=200；含版本等信息 | ✅已自动化 |
| TC-SYS-0005 | 初始化数据成功 | P0 | 正向 | 服务正常 | 1.GET /startup | code=200；数据库已初始化 | ✅已自动化 |
| TC-SYS-0006 | 访问首页成功 | P2 | 正向 | 服务正常 | 1.GET / | HTTP 200；返回HTML | ✅已自动化 |
| TC-SYS-0007 | 服务器信息-缺少自定义头 | P1 | 负向/安全 | 服务正常；有Token | 1.GET /info<br>2.只带Token | HTTP 403；缺少X-Custom-Key | ✅已自动化 |
| TC-SYS-0008 | 重复初始化数据 | P2 | 正向 | 服务正常 | 1.第一次/startup<br>2.第二次/startup | 两次都成功；数据一致 | ✅已自动化 |

---

## 附录

### A. 测试账号

| 用户名 | 密码(MD5) | 角色 | 用途 |
|--------|-----------|------|------|
| testuser | 482c811da5d5b4bc6d497ffa98491e38 | user | 普通用户测试 |
| admin | 21232f297a57a5a743894a0e4a801fc3 | admin | 管理员测试 |
| dept_manager | 482c811da5d5b4bc6d497ffa98491e38 | manager | 部门审批测试 |
| finance_manager | 482c811da5d5b4bc6d497ffa98491e38 | finance | 财务审批测试 |
| ceo | 482c811da5d5b4bc6d497ffa98491e38 | ceo | 总经理审批测试 |

### B. 自定义请求头

| 请求头 | 值 | 适用接口 |
|--------|-----|----------|
| X-Custom-Key | `mango_secret_key` | /health、/info |
| X-Request-Source | 任意非空字符串 | /health、/info |

### C. 接口依赖关系

```
登录获取Token
    ↓
业务接口（需要Token）
    ├── 用户管理 /users
    ├── 产品管理 /products
    ├── 订单管理 /orders（依赖用户、产品）
    ├── 审批流程 /reimbursements（依赖用户）
    ├── 数据提交 /api/data
    ├── 文件上传 /upload
    ├── 文件下载 /download/excel
    ├── 健康检查 /health（需要Token+自定义头）
    └── 服务器信息 /info（需要Token+自定义头）
```

### D. 字段说明

| 字段 | 说明 |
|------|------|
| **编号** | 用例唯一标识，格式 TC-{模块}-{序号} |
| **标题** | 一句话描述测试目的 |
| **优先级** | P0(阻塞)/P1(高)/P2(中) |
| **类型** | 正向/负向/边界/安全/集成/兼容 |
| **前置条件** | 执行用例前的准备工作 |
| **测试步骤** | 执行动作，每步用<br>分隔 |
| **预期结果** | 期望的响应和行为 |
| **自动化** | ✅已自动化 / ❌未自动化 |

