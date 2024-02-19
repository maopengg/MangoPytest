# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 
# @Time   : 2024-01-17 20:19
# @Author : 毛鹏
import pytest


def setup_module():
    print("这是一个setup_module")


def teardown_module():
    print("这是一个teardown_module")


def setup_function():
    print("这是一个setup_function")


def teardown_function():
    print("这是一个teardown_function")


def test_login():
    print("这是一个外部的方法")
    assert "admin" == "admin"


class TestDemo:

    def setup_class(self):
        print("这是一个setup_class")

    def teardown_class(self):
        print("这是一个teardown_class")

    def setup(self):
        print("这是一个setup")

    def teardown(self):
        print("这是一个teardown")

    def test_a(self):
        assert 2 == 2

    def test_b(self):
        assert 3 == 3

    def test_c(self):
        assert 5 == 5


if __name__ == '__main__':
    pytest.main()
