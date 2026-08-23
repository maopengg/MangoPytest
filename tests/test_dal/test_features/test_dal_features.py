"""
pytest-bdd feature 测试入口

运行 tests/test_dal/test_features/ 目录下的所有 .feature 文件
"""
from pytest_bdd import scenarios

# 自动发现并运行所有 feature 文件
scenarios('.')
