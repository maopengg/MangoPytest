# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-11 11:08
# @Author : 毛鹏
from config.get_path import ensure_path_sep

# 缓存文件路径
CACHE_PATH = ensure_path_sep("/static")
# 配置文件路径
CDXP_CONFING_PATH = ensure_path_sep("/project/cdxp/config.yml")
AIGC_CONFING_PATH = ensure_path_sep("/project/aigc/config.yml")
# 用例路径
AIGC_PATH = ensure_path_sep("/project/aigc/test_case")
CDXP_PATH = ensure_path_sep("/project/cdxp/test_case")

