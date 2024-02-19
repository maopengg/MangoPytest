# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023/4/6 13:36
# @Author : 毛鹏
from collections import Counter

from tools.assertion.public_assertion import PublicAssertion


class Assertion(PublicAssertion):

    @classmethod
    def ass_response_whole(cls, response_dict, case_ass):
        assert Counter(response_dict) == Counter(case_ass)
