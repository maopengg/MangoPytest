# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-19 10:07
# @Author : 毛鹏
from core.enums.tools_enum import EnvironmentEnum
from auto_tests.bdd_api_mock import PROJECT_NAME
from core.utils.main_run import MainRun

MainRun(
    project_config={
        'project': PROJECT_NAME,
        'test_environment': EnvironmentEnum.PROD,
    },
    pytest_command=[
        '-s',                                                   # 捕获 print 输出
        '-v',                                                   # 显示详细测试结果
        '-W',                                                   # 过滤警告
        'ignore:Module already imported:pytest.PytestWarning',  # 忽略重复导入警告
        '--alluredir', './report/tmp',                          # Allure 报告输出目录
        "--clean-alluredir",                                    # 运行前清空报告目录
        '-n 3',                                                 # 3 进程并行
        '--dist=loadscope',                                     # 按模块分配到进程
        '-p no:warnings',                                       # 不显示所有警告
    ],
).main()
