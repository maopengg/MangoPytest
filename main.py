# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-02-19 10:07
# @Author : 毛鹏
from auto_test.project_config import ProjectEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from tools.main_run import MainRun

"""
失败重试方式:
1、可在命令行 –reruns=1 reruns_delay=2 失败后重运行1次，延时2s
2、使用装饰器进行失败重运行
@pytest.mark.flaky(reruns=1, reruns_delay=2)
使用方式：
命令行参数：–reruns n（重新运行次数），–reruns-delay m（等待运行秒数）
装饰器参数：reruns=n（重新运行次数），reruns_delay=m（等待运行秒数）

    --reruns: 失败重跑次数
    --count: 重复执行次数
    -v: 显示错误位置以及错误的详细信息
    -s: 等价于 pytest --capture=no 可以捕获print函数的输出
    -q: 简化输出信息
    -m: 运行指定标签的测试用例
    -x: 一旦错误，则停止运行
    --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
    "--reruns=3", "--reruns-delay=2"
    -n 4: 代表使用多进程执行用例，4是进程数
    '--dist=loadscope',  # 确保每个文件在单独的进程中运行
    '-p no:warnings' 忽略警告
    'ignore:Module already imported:pytest.PytestWarning' 特定警告
    "--clean-alluredir",清空目录

"""
pytest_command = [
    '-s',
    '-v',
    '-W',
    'ignore:Module already imported:pytest.PytestWarning',
    '--alluredir',
    './report/tmp',
    "--clean-alluredir",
    '-n 5',
    '--dist=loadscope',
    '-p no:warnings'
]

test_project = [
    {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.UI},
    {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.API},
    {'project': ProjectEnum.BaiduTranslate, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.API},
    {'project': ProjectEnum.Gitee, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.UI},
    # {'project': ProjectEnum.Mango, 'test_environment': EnvironmentEnum.TEST, 'type': AutoTestTypeEnum.API},
]
MainRun(test_project=test_project, pytest_command=pytest_command)
