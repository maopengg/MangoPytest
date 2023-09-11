# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-11 11:08
# @Author : 毛鹏
from config.get_path import ensure_path_sep

# 缓存文件路径
CACHE_PATH = ensure_path_sep("/static")
# 用例路径
AIGC_PATH = ensure_path_sep("/project/aigc/test_case")
CDXP_PATH = ensure_path_sep("/project/cdxp/test_case")
# 每次报告存放地
REPORT_PATH = ensure_path_sep("/report")
# 压缩报告存放地
ZIP_REPORT_PATH = ensure_path_sep("/reports")

