# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-11 11:08
# @Author : 毛鹏
from tools.other_tools.path import Path

# 用例路径
AIGC_PATH = Path.ensure_path_sep("auto_test/api_project/aigc/test_case")
CDP_PATH = Path.ensure_path_sep("auto_test/api_project/cdxp/test_case")
AIGC_SAAS_PATH = Path.ensure_path_sep("auto_test/api_project/aigc_saas/test_case")

# 是否开启日志打印
PRINT_EXECUTION_RESULTS = True
# 请求超时失败时间
REQUEST_TIMEOUT_FAILURE_TIME = 60
SEND_USER: str
EMAIL_HOST: str
STAMP_KEY: str
