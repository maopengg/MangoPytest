# -*- coding: utf-8 -*-
from assertpy import assert_that


class PublicAssertion:
    """公共断言"""

    @classmethod
    def actual_large_expect(cls, actual, expect):
        """实际大于预期"""
        assert actual > expect

    @classmethod
    def is_null(cls, actual):
        """实际为None"""
        assert actual is None, f"实际：{actual}， 期望: 是null"

    @classmethod
    def is_not_none(cls, actual):
        """不是null"""
        assert_that(actual).is_not_none()

    @classmethod
    def is_empty(cls, actual):
        """是空"""
        assert_that(actual).is_empty()

    @classmethod
    def is_false(cls, actual):
        """是false"""
        assert_that(actual).is_false()

    @classmethod
    def is_type_of(cls, actual, expect):
        """判断类型"""
        assert_that(actual).is_type_of(eval(expect))

    @classmethod
    def is_instance_of(cls, actual, expect):
        """是实例-未测试"""
        assert_that(actual).is_instance_of(expect)

    @classmethod
    def is_length(cls, actual, expect):
        """是多长"""
        assert_that(actual).is_length(expect)

    @classmethod
    def is_not_empty(cls, actual):
        """不是空"""
        assert_that(actual).is_not_empty()

    @classmethod
    def is_true(cls, actual):
        """是true"""
        assert_that(actual).is_true()

    @classmethod
    def is_alpha(cls, actual):
        """是字母"""
        assert_that(actual).is_alpha()

    @classmethod
    def is_digit(cls, actual):
        """是数字"""
        assert_that(actual).is_digit()

    @classmethod
    def is_lower(cls, actual):
        assert_that(actual).is_lower()

    @classmethod
    def is_upper(cls, actual):
        """在什么上面"""
        assert_that(actual).is_upper()

    @classmethod
    def is_iterable(cls, actual):
        """是可迭代对象"""
        assert_that(actual).is_iterable()

    @classmethod
    def is_equal_to(cls, actual, expect):
        """等于"""
        assert_that(actual).is_equal_to(expect)

    @classmethod
    def is_not_equal_to(cls, actual, expect):
        """不等于"""
        assert_that(actual).is_not_equal_to(expect)

    @classmethod
    def is_equal_to_ignoring_case(cls, actual, expect):
        """忽略大小写等于"""
        assert_that(actual).is_equal_to_ignoring_case(expect)

    @classmethod
    def is_unicode(cls, actual):
        """是unicode"""
        assert_that(actual).is_unicode()

    @classmethod
    def contains(cls, actual, expect):
        """包含"""
        assert_that(actual).contains(**expect)

    @classmethod
    def contains_ignoring_case(cls, actual, expect):
        """包含忽略大小写"""
        assert_that(actual).contains_ignoring_case(expect)

    @classmethod
    def does_not_contain(cls, actual, expect):
        """不包含"""
        assert_that(actual).does_not_contain(expect)

    @classmethod
    def contains_only(cls, actual, expect):
        """仅包含"""
        assert_that(actual).contains_only(expect)

    @classmethod
    def contains_sequence(cls, actual, expect):
        """包含序列"""

        assert_that(actual).contains_sequence(expect)

    @classmethod
    def contains_duplicates(cls, actual):
        """仅包含"""
        assert_that(actual).contains_duplicates()

    @classmethod
    def does_not_contain_duplicates(cls, actual):
        """不包含重复项"""
        assert_that(actual).does_not_contain_duplicates()

    @classmethod
    def is_in(cls, actual, expect):
        """在里面"""
        assert_that(actual).is_in(**expect)

    @classmethod
    def is_not_in(cls, actual, expect):
        """不在里面"""
        assert_that(actual).is_not_in(expect)

    @classmethod
    def is_subset_of(cls, actual, expect):
        """在里面"""
        assert_that(actual).is_subset_of(expect)

    @classmethod
    def starts_with(cls, actual, expect):
        """以什么开头"""
        assert_that(actual).starts_with(expect)

    @classmethod
    def ends_with(cls, actual, expect):
        """以什么结尾"""
        assert_that(actual).ends_with(expect)

    @classmethod
    def matches(cls, actual, expect):
        """正则匹配"""
        assert_that(actual).matches(expect)

    @classmethod
    def does_not_match(cls, actual, expect):
        """正则不匹配"""
        assert_that(actual).does_not_match(expect)
