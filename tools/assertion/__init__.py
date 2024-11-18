# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏

from deepdiff import DeepDiff

from tools.assertion.public_assertion import PublicAssertion


class Assertion(PublicAssertion):

    @classmethod
    def ass_response_whole(cls, actual: dict, expect: dict):
        filtered_actual = {key: actual[key] for key in expect if key in actual}
        for key in expect.keys():
            if isinstance(expect[key], dict):
                if actual.get(key) is not None:
                    filtered_actual[key] = {k: actual[key][k] for k in expect[key] if k in actual[key]}
                else:
                    filtered_actual[key] = {}

        diff = DeepDiff(filtered_actual, expect, ignore_order=True)
        assert not diff, f"字典不匹配: {diff}"
