# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-10-07 15:27
# @Author : 毛鹏
import sqlite3

from test_run import TestRun  # 导入包含测试函数的模块
from tools.initialization import InitializationPath


# 连接到SQLite数据库
def connect_to_database():
    conn = sqlite3.connect(f'{InitializationPath.cache_path()}test_cases.db')
    return conn


# 从数据库中获取所有测试用例数据
def get_all_test_case_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_case")
    rows = cursor.fetchall()
    case_ids = [row[0] for row in rows]
    return case_ids


# 实例化TestRun类
test_run = TestRun()

# 连接到数据库
conn = connect_to_database()

# 获取所有测试用例数据
all_test_case_ids = get_all_test_case_data(conn)

# 循环执行测试函数，并生成测试报告
for case_id in all_test_case_ids:
    test_run.test_run(case_id, )

# 关闭数据库连接
conn.close()
