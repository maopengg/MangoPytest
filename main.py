#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2023/08/07 11:01
# @Author :
from auto_test.project_enum import ProjectEnum
from enums.tools_enum import EnvironmentEnum, AutoTestTypeEnum
from tools.main_run import MainRun

"""
    --reruns: 失败重跑次数
    --count: 重复执行次数
    -v: 显示错误位置以及错误的详细信息
    -s: 等价于 pytest --capture=no 可以捕获print函数的输出
    -q: 简化输出信息
    -m: 运行指定标签的测试用例
    -x: 一旦错误，则停止运行
    --maxfail: 设置最大失败次数，当超出这个阈值时，则不会在执行测试用例
    "--reruns=3", "--reruns-delay=2"
    -n 4: 代表使用多线程执行用例，4是线程数
    '-p no:warnings' 忽略警告
    'ignore:Module already imported:pytest.PytestWarning' 特定警告
    "--clean-alluredir",清空目录

"""
pytest_command = [
    '-s',
    '-W',
    'ignore:Module already imported:pytest.PytestWarning',
    '--alluredir',
    './report/tmp',
    "--clean-alluredir",
    '-n 3',
    '-v',
]

test_project = [
    {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.UI},
    # {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.API},
    # {'project': ProjectEnum.BaiduTranslate, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.API},
    # {'project': ProjectEnum.Gitee, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.UI},
    # {'project': ProjectEnum.Mango, 'test_environment': EnvironmentEnum.TEST, 'type': AutoTestTypeEnum.API},
]

if __name__ == '__main__':
    MainRun(test_project=test_project, pytest_command=pytest_command)
