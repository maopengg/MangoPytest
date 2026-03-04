# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏
import jsonschema
from deepdiff import DeepDiff
from jsonschema import validate

from tools.assertion.public_assertion import PublicAssertion
from tools.log import log

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
        assert not diff, f"预期：{expect}，实际：{filtered_actual}"
    @classmethod
    def ass_schema(cls, actual: dict, expect: dict):
        if actual and expect:
            log.debug(f'结构化断言->实际：{actual}，预期：{expect}')
            try:
                validate(instance=actual, schema=expect)
            except jsonschema.exceptions.ValidationError:
                assert False, f"结构化断言失败，实际：{actual}，预期：{expect}"