# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-08-11 11:08
# @Author : 毛鹏

# -------------------------------------是否开启调试-------------------------------------
IS_DEBUG = True

# ---------------------------------是否在运行结束后生成报告--------------------------------
IS_TEST_REPORT = True

# -------------------------------------API自动化配置-------------------------------------

PRINT_EXECUTION_RESULTS = True  # 是否开启日志打印
REQUEST_TIMEOUT_FAILURE_TIME = 60  # 请求超时失败时间

# --------------------------------------UI自动化配置-------------------------------------

BROWSER_IS_MAXIMIZE = True  # 是否开启UI自动化浏览器全屏

# -------------------------------UI元素自愈与AI配置---------------------------------

# 元素表只保存定位器和 AI 定位提示词；开关、模型和策略在系统设置统一管理。
ELEMENT_HEALING_ENABLED = True
ELEMENT_HEALING_MODE = 2
AI_ELEMENT_HEALING_ENABLED = False
AI_API_KEY = ""  # 不提交真实密钥；通过项目运行参数或环境变量注入
AI_BASE_URL = "https://api.siliconflow.cn/v1"
AI_MODEL = "THUDM/GLM-Z1-9B-0414"
AI_TIMEOUT = 30
AI_SEMANTIC_STRENGTH = 0

# ----------------------------------------邮件配置---------------------------------------

EMAIL_HOST = "smtp.qq.com"  # 发送邮件host，这个是QQ邮箱
SEND_USER = "2716185083@qq.com"  # 发送用户
STAMP_KEY = "jmuamgciqntydeji"  # 用户的key

# ------------------------------------全局请求代理设置------------------------------------

PROXY = {}  # 代理地址，如果没有就是空字典
