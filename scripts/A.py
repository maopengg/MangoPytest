# -*- coding: utf-8 -*-

import pytest


def data():
    return [('ha', 't', 'hat'), ('h', 'a', 'ha'), ('q', 'd', 'qd')]


class TestParamMore:
    @pytest.mark.parametrize("a, b, c", data())
    def test001(self, a, b, c):
        print(f"test001：{type(a)}-{type(b)}-{type(c)}")
        assert a + b == c
