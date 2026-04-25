# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 项目配置 - 手动指定测试环境
# @Time   : 2024-01-17 11:34
# @Author : 毛鹏

from core.enums import BaseEnum
from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum


# ==================== 项目枚举 ====================

class ProjectEnum(BaseEnum):
    """项目名称枚举 - 名称要和项目表的名称保持一致"""
    MOCK_API = 'MockAPI服务'
    MOCK_UI = 'MockUI服务'
    BAIDU = '百度'
    SQL = 'sql'
    PYTEST_API_MOCK = 'pytest_api_mock'
    BDD_API_MOCK = 'bdd_api_mock'


# ==================== 测试环境配置 ====================
# 手动指定各项目的执行环境
# 可选值: EnvironmentEnum.DEV / TEST / PRE / PRO

PROJECT_ENVIRONMENT = {
    ProjectEnum.MOCK_API: EnvironmentEnum.PRO,        # MockAPI服务 - 测试环境
    ProjectEnum.PYTEST_API_MOCK: EnvironmentEnum.DEV,  # pytest_api_mock - 开发环境
    ProjectEnum.BDD_API_MOCK: EnvironmentEnum.DEV,     # bdd_api_mock - 开发环境
    ProjectEnum.MOCK_UI: EnvironmentEnum.DEV,          # MockUI服务 - 生产环境
    ProjectEnum.BAIDU: EnvironmentEnum.PRO,            # 百度 - 生产环境
    ProjectEnum.SQL: EnvironmentEnum.PRO,              # SQL - 生产环境
}


# ==================== 项目基础配置 ====================

auto_test_project_config = [
    {'type': AutoTestTypeEnum.API, 'project_name': ProjectEnum.MOCK_API, 'dir_name': 'api_mock'},
    {'type': AutoTestTypeEnum.API, 'project_name': ProjectEnum.PYTEST_API_MOCK, 'dir_name': 'pytest_api_mock'},
    {'type': AutoTestTypeEnum.API, 'project_name': ProjectEnum.BDD_API_MOCK, 'dir_name': 'bdd_api_mock'},
    {'type': AutoTestTypeEnum.UI, 'project_name': ProjectEnum.MOCK_UI, 'dir_name': 'ui_mock'},
    {'type': AutoTestTypeEnum.UI, 'project_name': ProjectEnum.BAIDU, 'dir_name': 'ui_baidu'},
    {'type': AutoTestTypeEnum.OTHER, 'project_name': ProjectEnum.SQL, 'dir_name': 'sql_auto'},
]


# ==================== 工具函数 ====================

def get_project_environment(project_name: str) -> EnvironmentEnum:
    """
    获取项目指定的测试环境
    
    Args:
        project_name: 项目名称
        
    Returns:
        环境枚举值，未配置则返回 TEST
    """
    return PROJECT_ENVIRONMENT.get(project_name, EnvironmentEnum.TEST)


def set_os_environment(project_name: str) -> None:
    """
    设置操作系统环境变量（供项目配置读取）
    
    Args:
        project_name: 项目名称
    """
    import os
    
    env = get_project_environment(project_name)
    
    # 将 EnvironmentEnum 转换为字符串
    env_map = {
        EnvironmentEnum.DEV: 'dev',
        EnvironmentEnum.TEST: 'test',
        EnvironmentEnum.PRE: 'pre',
        EnvironmentEnum.PRO: 'prod',
    }
    
    env_str = env_map.get(env, 'test')
    os.environ['ENV'] = env_str
    
    # 打印日志
    print(f"[项目: {project_name}] 设置执行环境: {env_str}")
