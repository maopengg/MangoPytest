# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-11 11:08
# @Author : 毛鹏
from models.tools_model import MysqlConingModel
from tools.other_tools.path import Path

# 测试平台的的mysql配置
AUTO_TEST_MYSQL_DB = MysqlConingModel(host='61.183.9.60', port=23306, user='root', password='zALL_mysql1',
                                      database='aigc_AutoTestPlatform')
# 用例路径
AIGC_PATH = Path.ensure_path_sep("auto_test/api_project/aigc/test_case")
CDP_PATH = Path.ensure_path_sep("auto_test/api_project/cdxp/test_case")
AIGC_SAAS_PATH = Path.ensure_path_sep("auto_test/api_project/aigc_saas/test_case")

# 是否开启日志打印
PRINT_EXECUTION_RESULTS = True
