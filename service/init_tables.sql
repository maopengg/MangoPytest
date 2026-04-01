-- ========================================================
-- Mango Mock API 数据库初始化脚本
-- 数据库: mango_mock
-- 作者: 毛鹏
-- 日期: 2026-04-01
-- ========================================================

-- 使用数据库
USE mango_mock;

-- ========================================================
-- 1. 用户表 (users)
-- ========================================================
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    full_name VARCHAR(100) NOT NULL COMMENT '全名',
    password VARCHAR(255) NOT NULL COMMENT '密码(MD5加密)',
    role ENUM('user', 'admin', 'manager', 'finance', 'ceo') DEFAULT 'user' COMMENT '角色',
    status ENUM('active', 'inactive', 'deleted') DEFAULT 'active' COMMENT '状态',
    last_login_at DATETIME DEFAULT NULL COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ========================================================
-- 2. 产品表 (products)
-- ========================================================
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '产品ID',
    name VARCHAR(200) NOT NULL COMMENT '产品名称',
    price DECIMAL(10, 2) NOT NULL COMMENT '价格',
    description TEXT COMMENT '产品描述',
    stock INT DEFAULT 0 COMMENT '库存数量',
    category VARCHAR(50) DEFAULT 'general' COMMENT '产品分类',
    status ENUM('active', 'inactive', 'deleted') DEFAULT 'active' COMMENT '状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_category (category),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品表';

-- ========================================================
-- 3. 订单表 (orders)
-- ========================================================
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单ID',
    order_no VARCHAR(50) NOT NULL UNIQUE COMMENT '订单编号',
    product_id INT NOT NULL COMMENT '产品ID',
    user_id INT NOT NULL COMMENT '用户ID',
    quantity INT NOT NULL COMMENT '数量',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT '单价',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '总金额',
    status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled') DEFAULT 'pending' COMMENT '订单状态',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_order_no (order_no),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ========================================================
-- 4. 数据提交表 (data_submissions)
-- ========================================================
DROP TABLE IF EXISTS data_submissions;

CREATE TABLE data_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '提交ID',
    name VARCHAR(100) NOT NULL COMMENT '数据名称',
    value INT NOT NULL COMMENT '数据值',
    submitter_id INT DEFAULT NULL COMMENT '提交者ID',
    source_ip VARCHAR(50) DEFAULT NULL COMMENT '来源IP',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_name (name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据提交表';

-- ========================================================
-- 5. 文件上传表 (files)
-- ========================================================
DROP TABLE IF EXISTS files;

CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '文件ID',
    file_id VARCHAR(50) NOT NULL UNIQUE COMMENT '文件唯一标识',
    filename VARCHAR(255) NOT NULL COMMENT '文件名',
    original_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    content_type VARCHAR(100) DEFAULT NULL COMMENT '文件类型',
    size INT DEFAULT 0 COMMENT '文件大小(字节)',
    file_path VARCHAR(500) DEFAULT NULL COMMENT '文件存储路径',
    uploader_id INT DEFAULT NULL COMMENT '上传者ID',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_file_id (file_id),
    INDEX idx_uploader (uploader_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传表';

-- ========================================================
-- 6. 报销申请表 (reimbursements)
-- ========================================================
DROP TABLE IF EXISTS reimbursements;

CREATE TABLE reimbursements (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '报销ID',
    reimb_no VARCHAR(50) NOT NULL UNIQUE COMMENT '报销单号',
    user_id INT NOT NULL COMMENT '申请人ID',
    amount DECIMAL(12, 2) NOT NULL COMMENT '报销金额',
    reason TEXT NOT NULL COMMENT '报销原因',
    category VARCHAR(50) DEFAULT 'general' COMMENT '报销类别',
    attachments TEXT COMMENT '附件列表(JSON)',
    status ENUM('pending', 'dept_approved', 'dept_rejected', 'finance_approved', 'finance_rejected', 'ceo_approved', 'ceo_rejected', 'paid') DEFAULT 'pending' COMMENT '审批状态',
    current_step TINYINT DEFAULT 1 COMMENT '当前步骤(1-D级,2-C级,3-B级,4-A级)',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    completed_at DATETIME DEFAULT NULL COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_reimb_no (reimb_no),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报销申请表';

-- ========================================================
-- 7. 部门审批表 (dept_approvals) - C级审批
-- ========================================================
DROP TABLE IF EXISTS dept_approvals;

CREATE TABLE dept_approvals (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '审批ID',
    approval_no VARCHAR(50) NOT NULL UNIQUE COMMENT '审批单号',
    reimbursement_id INT NOT NULL COMMENT '报销申请ID',
    approver_id INT NOT NULL COMMENT '审批人ID',
    status ENUM('approved', 'rejected') NOT NULL COMMENT '审批结果',
    comment TEXT COMMENT '审批意见',
    approved_at DATETIME DEFAULT NULL COMMENT '审批时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (reimbursement_id) REFERENCES reimbursements(id) ON DELETE CASCADE,
    FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_reimbursement_id (reimbursement_id),
    INDEX idx_approver_id (approver_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门审批表';

-- ========================================================
-- 8. 财务审批表 (finance_approvals) - B级审批
-- ========================================================
DROP TABLE IF EXISTS finance_approvals;

CREATE TABLE finance_approvals (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '审批ID',
    approval_no VARCHAR(50) NOT NULL UNIQUE COMMENT '审批单号',
    reimbursement_id INT NOT NULL COMMENT '报销申请ID',
    dept_approval_id INT NOT NULL COMMENT '部门审批ID',
    approver_id INT NOT NULL COMMENT '审批人ID',
    status ENUM('approved', 'rejected') NOT NULL COMMENT '审批结果',
    comment TEXT COMMENT '审批意见',
    finance_check_passed BOOLEAN DEFAULT FALSE COMMENT '财务核查通过',
    approved_at DATETIME DEFAULT NULL COMMENT '审批时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (reimbursement_id) REFERENCES reimbursements(id) ON DELETE CASCADE,
    FOREIGN KEY (dept_approval_id) REFERENCES dept_approvals(id) ON DELETE RESTRICT,
    FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_reimbursement_id (reimbursement_id),
    INDEX idx_dept_approval_id (dept_approval_id),
    INDEX idx_approver_id (approver_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='财务审批表';

-- ========================================================
-- 9. 总经理审批表 (ceo_approvals) - A级审批
-- ========================================================
DROP TABLE IF EXISTS ceo_approvals;

CREATE TABLE ceo_approvals (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '审批ID',
    approval_no VARCHAR(50) NOT NULL UNIQUE COMMENT '审批单号',
    reimbursement_id INT NOT NULL COMMENT '报销申请ID',
    finance_approval_id INT NOT NULL COMMENT '财务审批ID',
    approver_id INT NOT NULL COMMENT '审批人ID',
    status ENUM('approved', 'rejected') NOT NULL COMMENT '审批结果',
    comment TEXT COMMENT '审批意见',
    approved_at DATETIME DEFAULT NULL COMMENT '审批时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (reimbursement_id) REFERENCES reimbursements(id) ON DELETE CASCADE,
    FOREIGN KEY (finance_approval_id) REFERENCES finance_approvals(id) ON DELETE RESTRICT,
    FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_reimbursement_id (reimbursement_id),
    INDEX idx_finance_approval_id (finance_approval_id),
    INDEX idx_approver_id (approver_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='总经理审批表';

-- ========================================================
-- 10. 审批流程日志表 (approval_logs)
-- ========================================================
DROP TABLE IF EXISTS approval_logs;

CREATE TABLE approval_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    reimbursement_id INT NOT NULL COMMENT '报销申请ID',
    step TINYINT NOT NULL COMMENT '审批步骤(1-4)',
    step_name VARCHAR(50) NOT NULL COMMENT '步骤名称',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    operator_id INT NOT NULL COMMENT '操作人ID',
    operator_name VARCHAR(100) COMMENT '操作人姓名',
    comment TEXT COMMENT '操作备注',
    old_status VARCHAR(50) COMMENT '原状态',
    new_status VARCHAR(50) COMMENT '新状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (reimbursement_id) REFERENCES reimbursements(id) ON DELETE CASCADE,
    INDEX idx_reimbursement_id (reimbursement_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批流程日志表';

-- ========================================================
-- 11. API调用日志表 (api_logs)
-- ========================================================
DROP TABLE IF EXISTS api_logs;

CREATE TABLE api_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    request_id VARCHAR(50) NOT NULL COMMENT '请求ID',
    method VARCHAR(10) NOT NULL COMMENT '请求方法',
    path VARCHAR(255) NOT NULL COMMENT '请求路径',
    query_params TEXT COMMENT '查询参数',
    request_body TEXT COMMENT '请求体',
    response_body TEXT COMMENT '响应体',
    status_code INT COMMENT '响应状态码',
    user_id INT DEFAULT NULL COMMENT '用户ID',
    client_ip VARCHAR(50) COMMENT '客户端IP',
    user_agent VARCHAR(500) COMMENT '用户代理',
    duration_ms INT COMMENT '执行时长(毫秒)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_request_id (request_id),
    INDEX idx_path (path),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API调用日志表';

-- ========================================================
-- 初始化数据
-- ========================================================

-- 初始化用户数据
-- 密码说明:
-- testuser, dept_manager, finance_manager, ceo: 482c811da5d5b4bc6d497ffa98491e38 = 'password123'
-- admin: 21232f297a57a5a743894a0e4a801fc3 = 'admin'

INSERT INTO users (id, username, email, full_name, password, role, status, created_at, updated_at) VALUES
(1, 'testuser', 'test@example.com', 'Test User', '482c811da5d5b4bc6d497ffa98491e38', 'user', 'active', NOW(), NOW()),
(2, 'admin', 'admin@example.com', 'Administrator', '21232f297a57a5a743894a0e4a801fc3', 'admin', 'active', NOW(), NOW()),
(3, 'dept_manager', 'dept@example.com', 'Department Manager', '482c811da5d5b4bc6d497ffa98491e38', 'manager', 'active', NOW(), NOW()),
(4, 'finance_manager', 'finance@example.com', 'Finance Manager', '482c811da5d5b4bc6d497ffa98491e38', 'finance', 'active', NOW(), NOW()),
(5, 'ceo', 'ceo@example.com', 'CEO', '482c811da5d5b4bc6d497ffa98491e38', 'ceo', 'active', NOW(), NOW()),
(6, 'zhangsan', 'zhangsan@example.com', '张三', '482c811da5d5b4bc6d497ffa98491e38', 'user', 'active', NOW(), NOW()),
(7, 'lisi', 'lisi@example.com', '李四', '482c811da5d5b4bc6d497ffa98491e38', 'user', 'active', NOW(), NOW()),
(8, 'wangwu', 'wangwu@example.com', '王五', '482c811da5d5b4bc6d497ffa98491e38', 'user', 'inactive', NOW(), NOW());

-- 初始化产品数据
INSERT INTO products (name, price, description, stock, category, status, created_at, updated_at) VALUES
('笔记本电脑', 5999.00, '高性能商务笔记本，Intel i7处理器，16GB内存，512GB SSD', 100, 'electronics', 'active', NOW(), NOW()),
('无线鼠标', 99.00, '人体工学设计，2.4G无线连接，静音按键', 200, 'accessories', 'active', NOW(), NOW()),
('机械键盘', 399.00, 'RGB背光，青轴，全键无冲', 150, 'accessories', 'active', NOW(), NOW()),
('显示器', 1299.00, '27英寸4K超高清，IPS面板，HDR400', 50, 'electronics', 'active', NOW(), NOW()),
('USB-C扩展坞', 299.00, '七合一扩展坞，支持4K输出，PD快充', 80, 'accessories', 'active', NOW(), NOW()),
('降噪耳机', 899.00, '主动降噪，40小时续航，蓝牙5.0', 60, 'audio', 'active', NOW(), NOW()),
('移动硬盘', 459.00, '2TB容量，USB3.0接口，轻薄便携', 120, 'storage', 'active', NOW(), NOW()),
('打印机', 1299.00, '激光打印，无线连接，自动双面', 30, 'office', 'inactive', NOW(), NOW());

-- 设置自增ID起始值
ALTER TABLE users AUTO_INCREMENT = 100;
ALTER TABLE products AUTO_INCREMENT = 100;
ALTER TABLE orders AUTO_INCREMENT = 1000;
ALTER TABLE reimbursements AUTO_INCREMENT = 1000;
ALTER TABLE dept_approvals AUTO_INCREMENT = 100;
ALTER TABLE finance_approvals AUTO_INCREMENT = 100;
ALTER TABLE ceo_approvals AUTO_INCREMENT = 100;

-- ========================================================
-- 完成
-- ========================================================
SELECT '数据库初始化完成!' AS message;
