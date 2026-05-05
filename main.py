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

# =============================================================================
# 参数速查（按需添加到 pytest_command 中）
# =============================================================================
#
# [pytest 核心参数]
#   -s                          捕获 print 输出
#   -v                          显示详细测试结果
#   -W                          过滤警告
#   -k EXPRESSION              按名称过滤测试用例
#   -m MARKEXPR                按 marker 过滤测试用例
#   --tb=style                 控制 traceback 显示 (auto/long/short/line/native/no)
#   --maxfail=num              失败 N 次后停止
#   --durations=N              显示最慢的 N 个测试
#   --co / --collect-only      仅收集用例不执行，显示用例列表
#   -p no:warnings             不显示所有警告
#
# [pytest-rerunfailures 插件]
#   --reruns NUM               失败重试次数
#   --reruns-delay SECONDS     重试间隔秒数
#
# [pytest-xdist 插件]
#   -n NUM                     并行进程数 (auto 表示自动)
#   --dist=mode                分发模式 (load/loadfile/loadscope/no)
#   --tx NUM*SPEC              指定执行节点
#
# [allure-pytest 插件]
#   --alluredir DIR            Allure 报告输出目录
#   --clean-alluredir          运行前清空报告目录
#   --allure-no-capture        禁用 Allure 捕获 log/stdout/stderr 附件
#   --allure-link-pattern      自定义链接模板
#   --allure-severities        按严重级别过滤用例
#   --allure-features          按 feature 过滤用例
#   --allure-stories           按 story 过滤用例
#   --allure-epics             按 epic 过滤用例
#   --allure-labels            按 label 过滤用例
# =============================================================================
