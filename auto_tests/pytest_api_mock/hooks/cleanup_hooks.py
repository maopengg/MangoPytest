# -*- coding: utf-8 -*-
"""pytest_api_mock 测试数据清理。"""

from typing import Iterable

import pymysql

from auto_tests.pytest_api_mock.config import settings
from core.utils import log


def _like_any(column: str, values: Iterable[str]) -> tuple[str, list[str]]:
    conditions = [f"{column} LIKE %s" for _ in values]
    return " OR ".join(conditions), list(values)


def cleanup_auto_test_data() -> None:
    """按依赖顺序清理自动化测试产生的数据。"""
    config = {
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "database": settings.DB_NAME,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }

    product_patterns = [
        "AUTO\\_%", "Product %", "iPhone 15", "Test Product", "MacBook Pro",
        "无线耳机", "办公椅", "批量产品\\_%", "Original Name",
        "库存测试产品", "零库存产品", "删除测试产品\\_%"
    ]
    user_patterns = [
        "AUTO\\_%", "test_user\\_%", "admin\\_%", "dept\\_%", "finance\\_%",
        "ceo\\_%", "dup_test\\_%", "newuser\\_%", "batch_user\\_%"
    ]
    data_patterns = [
        "AUTO\\_%", "test_metric", "test_data", "zero_value", "large_value",
        "negative_value", "中文名称", "name with spaces", "name_with-special.chars",
        "query测试", "body值", "测试数据"
    ]
    file_patterns = [
        "AUTO\\_%", "test\\_%", "test_file%", "测试上传文件.txt", "中文文件.txt",
        "file with spaces.txt", "test.pdf", "data.json", "builder_test.txt"
    ]

    conn = None
    try:
        conn = pymysql.connect(**config)
        with conn.cursor() as cursor:
            total = 0

            for table in ("ceo_approvals", "finance_approvals", "dept_approvals"):
                total += cursor.execute(f"DELETE FROM {table} WHERE id >= 100")

            total += cursor.execute("DELETE FROM reimbursements WHERE id >= 1000")
            total += cursor.execute("DELETE FROM orders WHERE id >= 1000")

            condition, params = _like_any("name", data_patterns)
            total += cursor.execute(f"DELETE FROM data_submissions WHERE {condition}", params)

            condition, params = _like_any("filename", file_patterns)
            total += cursor.execute(f"DELETE FROM files WHERE {condition}", params)

            condition, params = _like_any("name", product_patterns)
            total += cursor.execute(f"DELETE FROM products WHERE id >= 100 AND ({condition})", params)

            condition, params = _like_any("username", user_patterns)
            total += cursor.execute(f"DELETE FROM users WHERE id >= 100 AND ({condition})", params)

        conn.commit()
        log.info(f">>> [pytest_api_mock cleaner] 清理完成，共删除 {total} 条记录")
    except Exception as exc:
        if conn:
            conn.rollback()
        log.warning(f">>> [pytest_api_mock cleaner] 清理失败: {exc}")
    finally:
        if conn:
            conn.close()
