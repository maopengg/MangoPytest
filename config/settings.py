# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-11 11:08
# @Author : 毛鹏
from config.get_path import ensure_path_sep
from models.tools_model import MysqlConingModel

# 测试平台的的mysql配置
AUTO_TEST_MYSQL_DB = MysqlConingModel(host='61.183.9.60', port=23306, user='root', password='zALL_mysql1',
                                  database='aigc_AutoTestPlatform')
# 用例路径
AIGC_PATH = ensure_path_sep("/project/aigc/test_case")
CDXP_PATH = ensure_path_sep("/project/cdxp/test_case")
AIGC_SAAS_PATH = ensure_path_sep("/project/aigc_saas/test_case")
# 每次报告存放地
REPORT_PATH = ensure_path_sep("/report")
# 压缩报告存放地
ZIP_REPORT_PATH = ensure_path_sep("/reports")

# 是否开启日志打印
PRINT_EXECUTION_RESULTS = True
