# -*- coding: utf-8 -*-
"""
Factory 工具函数
"""

import random
import string
from datetime import datetime


def generate_auto_id():
    """生成 AUTO_ 前缀的随机ID
    
    格式: AUTO_<timestamp>_<random_suffix>
    例如: AUTO_20240422153045_ABC123
    
    用于:
    1. 标识自动化测试生成的数据
    2. 测试后自动清理
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{timestamp}_{random_suffix}"


def auto_username(role: str = "USER"):
    """生成 AUTO_ 前缀的用户名"""
    return f"AUTO_{role}_{generate_auto_id()}"


def auto_product_name():
    """生成 AUTO_ 前缀的产品名"""
    return f"AUTO_PRODUCT_{generate_auto_id()}"


def auto_order_no():
    """生成 AUTO_ 前缀的订单号"""
    return f"AUTO_ORDER_{generate_auto_id()}"


def auto_reimbursement_no():
    """生成 AUTO_ 前缀的报销单号"""
    return f"AUTO_REIM_{generate_auto_id()}"


def auto_filename():
    """生成 AUTO_ 前缀的文件名"""
    return f"AUTO_FILE_{generate_auto_id()}.txt"


def auto_data_title():
    """生成 AUTO_ 前缀的数据标题"""
    return f"AUTO_DATA_{generate_auto_id()}"
