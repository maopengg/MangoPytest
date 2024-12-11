# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏

from deepdiff import DeepDiff

from tools.assertion.public_assertion import PublicAssertion


def filter_dict(actual: dict, expect: dict) -> dict:
    filtered = {}
    for key in expect.keys():
        if key in actual:
            if isinstance(expect[key], dict):
                filtered[key] = filter_dict(actual[key], expect[key])
            elif isinstance(expect[key], list) and isinstance(actual[key], list):
                filtered[key] = []
                for item in actual[key]:
                    if isinstance(item, dict):
                        filtered_item = filter_dict(item, expect[key][0])
                        filtered[key].append(filtered_item)
                    else:
                        filtered[key].append(item)
            else:
                filtered[key] = actual[key]
    return filtered


class Assertion(PublicAssertion):

    @classmethod
    def ass_response_whole(cls, actual: dict, expect: dict):
        filtered_actual = filter_dict(actual, expect)
        diff = DeepDiff(filtered_actual, expect, ignore_order=True)
        assert not diff, f"字典不匹配: {diff}"
